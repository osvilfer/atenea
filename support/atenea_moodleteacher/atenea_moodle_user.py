# -*- coding: utf-8 -*-
from moodleteacher.users import MoodleUser
from moodleteacher.requests import MoodleRequest

import logging

_logger = logging.getLogger(__name__)

class ContinueOutter(Exception):
    pass

continue_outter = ContinueOutter()

class AteneaMoodleUser(MoodleUser):
  """
  Amplia los datos que se obtienen de un usuario

  Hereda de MoodleUser
  """
  
  # nuevos atributos
  username = None
  lastname = None
  firstname = None
  roles = None

  @classmethod
  def from_userid(cls, conn, user_id):
    obj = cls()
    obj.id_ = user_id
    params = {'field': 'id', 'values[0]': str(user_id)}
    response = MoodleRequest(
      conn, 'core_user_get_users_by_field').post(params).json()
    if response != []:
      assert(response[0]['id'] == user_id)

      obj.fullname = response[0]['fullname']
      obj.email = response[0]['email']
      #obj.username = response[0]['username']
      obj.lastname = response[0]['lastname']
      obj.firstname = response[0]['firstname']
    else:
      obj.fullname = "<Unknown>"
      obj.email = "<Unknown>"
      #obj.username = "<Unknown>"
      obj.lastname = "<Unknown>"
      obj.firstname = "<Unknown>"
   
    return obj


  @classmethod
  def from_raw_json(cls, raw_json):
    """
    Crea un :class:`AteneaMoodleUser` objeto desde un JSON
    """

    obj = cls()
    obj.id_ = raw_json['id_']
    obj.firstname = raw_json['firstname']
    obj.lastname = raw_json['lastname']
    obj.email = raw_json['email']
 
    return obj
  
class AteneaMoodleUsers(list):
  """
  Una lista de instancias de la :class:`AteneaMoodleUser`.
  """

  def __init__(self):
    list.__init__(self)

  @classmethod
  def from_course(cls, conn, course_id, only_students = False):
    """
    Genera una lista de participantes de un curso (de un aula virtual, classroom para atenea)
    """
    obj = cls()

    params = {}
    params['courseid'] = course_id
    try:
      response = MoodleRequest(
        conn, 'core_enrol_get_enrolled_users').get(params).json()
    except Exception as e:
      raise Exception("Excepción [core_enrol_get_enrolled_users]: " + str(e))
    

    for st in response:
      st_json =  {
        'id_': st['id'],
        'firstname': st['firstname'],
        'lastname': st['lastname'],
        'email': st['email'],
      }

      roles = []
      for rol in st['roles']:
        roles.append(rol['shortname'])

      if only_students:
        try:
          for s in roles:
            if 'teacher' in s:
              raise continue_outter
        except ContinueOutter:
          continue
      else:
        st_json['roles'] = roles

      student = AteneaMoodleUser.from_raw_json(st_json)
      obj.append(student)

    return obj