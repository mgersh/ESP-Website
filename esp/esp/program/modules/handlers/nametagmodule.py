
__author__    = "MIT ESP"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "GPL v.2"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2007 MIT ESP

The ESP Web Site is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

Contact Us:
ESP Web Group
MIT Educational Studies Program,
84 Massachusetts Ave W20-467, Cambridge, MA 02139
Phone: 617-253-4882
Email: web@esp.mit.edu
"""
from esp.program.modules.base import ProgramModuleObj, needs_teacher, needs_student, needs_admin, usercheck_usetl, main_call, aux_call
from esp.program.modules import module_ext
from esp.web.util        import render_to_response
from django.contrib.auth.decorators import login_required
from esp.users.models import ESPUser, User
from django.db.models.query import Q
from esp.users.views  import get_user_list
from esp.middleware import ESPError
from esp.web.util.latex import render_to_latex

class NameTagModule(ProgramModuleObj):
    """ This module allows you to generate a bunch of IDs for everyone in the program. """
    @classmethod
    def module_properties(cls):
        return {
            "link_title": "Generate Nametags",
            "module_type": "manage",
            "seq": 100
            }

    @main_call
    @needs_admin
    def selectidoptions(self, request, tl, one, two, module, extra, prog):
        """ Display a teacher eg page """
        context = {'module': self}

        return render_to_response(self.baseDir()+'selectoptions.html', request, (prog, tl), context)

    @aux_call
    @needs_admin
    def generatestickers(self, request, tl, one, two, module, extra, prog):
        timeslots = prog.getTimeSlots()
        students = prog.students()['confirmed']
        context = {'timeslots': timeslots, 'students': students}
        if request.GET.has_key("format"):
            format = request.GET["format"]
        else:
            format = "pdf"

        zipped_list = []

        students = list(students)

        while students != []:
            zipped_list.append(students[:3])
            students = students[3:]

        context['zipped_list'] = zipped_list

        return render_to_latex(self.baseDir()+'stickers.tex', context, format)

    @aux_call
    @needs_admin
    def generatetags(self, request, tl, one, two, module, extra, prog):
        """ generate nametags """

        # Default to students
        if 'type' not in request.POST:
            raise ESPError(log=False), "You need to select the TYPE of Name Tag to print. (students,teachers,etc)"
        idtype = request.POST['type']

        users = []


        if idtype == 'students':
            student_dict = self.program.students(QObjects = True)
            if 'classreg' in student_dict:
                students = User.objects.filter(student_dict['classreg'] | student_dict['confirmed']).distinct()
            else:
                students = User.objects.filter(student_dict['confirmed']).distinct()

            students = [ ESPUser(student) for student in
                         students ]

            students = filter(lambda x: len(x.first_name+x.last_name), students)
            students.sort()


            for student in students:
                users.append({'title': 'Student',
                              'name' : '%s %s' % (student.first_name, student.last_name),
                              'id'   : student.id})

        elif idtype == 'teacher':
            teachers = []
            teacher_dict = self.program.teachers(QObjects=True)
            teachers = User.objects.filter(teacher_dict['class_approved']).distinct()
#            teachers = User.objects.filter(teacher_dict['teacher_profile'] | teacher_dict['class_rejected']).distinct()

	    teachers = [ ESPUser(teacher) for teacher in teachers ]
            teachers = filter(lambda x: len(x.first_name+x.last_name), teachers)
            teachers.sort()

            for teacher in teachers:
                users.append({'title': 'Teacher',
                              'name' : '%s %s' % (teacher.first_name, teacher.last_name),
                              'id'   : teacher.id})

        elif idtype == 'volunteers':
            users = []
            volunteers = request.POST['volunteers']
            for user in volunteers.split("\n"):
                arruser = user.split(",", 1)

                if len(arruser) >= 2:
                    users.append({'title': arruser[1].strip(),
                                  'name' : arruser[0].strip(),
                                  'id'   : ''})


        elif idtype == 'blank':
            users = []
            for i in range(int(request.POST['number'])):
                users.append({'title': request.POST['blanktitle'],
                              'name' : '',
                              'id'   : ''})

        context = {'module': self,
                   'programname': request.POST['progname']
                   }


        numperpage = 6


        expanded = [[] for i in range(numperpage)]

        for i in range(len(users)):
            expanded[(i*numperpage)/len(users)].append(users[i])

        users = []

        for i in range(len(expanded[0])):
            for j in range(len(expanded)):
                if len(expanded[j]) <= i:
                    users.append({'title': 'Student',
                                  'name' : '',
                                  'id'   : ''})
                else:
                    users.append(expanded[j][i])

        context['users'] = users

        return render_to_response(self.baseDir()+'ids.html', request, (prog, tl), context)


