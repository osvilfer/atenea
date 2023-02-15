# -*- coding: utf-8 -*-

import datetime
from odoo import api, models, fields
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class SchoolYear(models.Model):
  """
  Define información del curso escolar
  """
      
  _name = 'atenea.school_year'
  _description = 'Curso escolar'

  name = fields.Char(readonly = True, compute = '_compute_name', string = 'Curso')
  state = fields.Selection([
      ('0', 'Borrador'),
      ('1', 'En curso'),
      ('2', 'Finalizado')
      ], string ='Estado del curso', default = '0')
  
  date_init = fields.Date(string='Fecha de incio oficial')

  # estructura de datos con las fechas 
  dates = { 'init_lective': { 'date': '', 'desc': 'Inicio clases', 'type': 'G'}}

  # inicio real de las clases
  date_init_lective = fields.Date(string = 'Fecha de inicio real', compute = '_compute_date_init_lective', readonly = False, store = True)
  # jornadas de bienvenida
  date_welcome_day = fields.Date(string = 'Jornadas de bienvenida', compute = '_compute_welcome_day', store = True)
  # SEGUNDO
  # fin de las clases de la primera evaluación de segundo
  date_1term2_end = fields.Date(string = 'Fin clases primera evaluación', compute = '_compute_1term2_end', readonly = False, store = True) 
  # inicio examenes 1 evaluación de segundo. En caso de readonly True hay que forzar su grabación en el XML con force_save
  date_1term2_exam_ini = fields.Date(string = 'Inicio exámenes primera evaluación', compute = '_compute_1term2_exam_ini', readonly = False, store = True) 
  # fin exámenes 1 evaluación de segundo
  date_1term2_exam_end = fields.Date(string = 'Fin exámenes primera evaluación', compute = '_compute_1term2_exam_end', store = True) 
  # duración primera evaluación segundo
  duration_1term2 = fields.Integer(string = 'Duración (semanas)', compute = '_compute_duration_1term2')
  # inicio segunda evaluación
  date_2term2_ini = fields.Date(string = 'Inicio segunda evaluación', compute = '_compute_2term2_ini', store = True) 
  # fin de las clases de la segunda evaluación de segundo
  date_2term2_end = fields.Date(string = 'Fin clases segunda evaluación', compute = '_compute_2term2_end', readonly = False, store = True) 
  # inicio examenes 2 evaluación de segundo
  date_2term2_exam_ini = fields.Date(string = 'Inicio exámenes segunda evaluación', compute = '_compute_2term2_exam_ini', readonly = False, store = True) 
  # fin exámenes 2 evaluación de segundo
  date_2term2_exam_end = fields.Date(string = 'Fin exámenes segunda evaluación', compute = '_compute_2term2_exam_end', store = True) 
  # duración segunda evaluación segundo
  duration_2term2 = fields.Integer(string = 'Duración (semanas)', compute = '_compute_duration_2term2')
  # inicio examenes ordinaria de segundo
  date_ord2_exam_ini = fields.Date(string = 'Inicio exámenes ordinaria', compute = '_compute_ord2_exam_ini', readonly = False, store = True) 
  # fin exámenes ordinaria de segundo
  date_ord2_exam_end = fields.Date(string = 'Fin exámenes ordinaria', compute = '_compute_ord2_exam_end', store = True) 
  # inicio examenes ordinaria de segundo
  date_extraord2_exam_ini = fields.Date(string = 'Inicio exámenes extraordinaria') #, compute = '_compute_extraord2_exam_ini', readonly = False, store = True) 
  # fin exámenes ordinaria de segundo
  date_extraord2_exam_end = fields.Date(string = 'Fin exámenes extraordinaria') #, compute = '_compute_extraord2_exam_end', store = True) 
  # anulación de matrícula
  date_cancellation2 = fields.Date(string = 'Fin anulación de matrícula', compute = '_compute_cancellation2') 
  # renuncia convocatoria ordinaria
  date_waiver_ord2 = fields.Date(string = 'Fin renuncia convocatoria ordinaria', compute = '_compute_waiver_ord2') 
  # renuncia convocatoria extraordinaria
  date_waiver_extraord2 = fields.Date(string = 'Fin renuncia convocatoria extraordinaria', compute = '_compute_waiver_extraord2') 


  holidays_ids = fields.One2many('atenea.holiday', 'school_year_id')

  # report calendario escolar  
  school_calendar_version = fields.Integer(string = 'Versión calendario escolar', default = 1, store = True, readonly = True)
  school_calendar_update_keys = ['init_lective', 'date_init_lective', 'date_welcome_day', 'date_1term2_end', 
    'date_1term2_exam_ini', 'date_1term2_exam_end', 'date_2term2_ini', 'date_2term2_end', 'date_ord2_exam_ini',
    'date_ord2_exam_end','date_extraord2_exam_ini', 'date_extraord2_exam_end']

  # TODO: constraints para que se mantenga el orden cronológico de las fechas

  """ Sobreescritura de la función create que es llamada cuando se crea un registro nuevo """
  @api.model
  def create(self, vals):
    # la primera versión de los informes se crea al crear el registro
    vals['school_calendar_version'] = 1
    res_id = super(SchoolYear, self).create(vals)
    return res_id

  """ Sobreescritura de la función write que es llamada cuando se actualiza un registro """
  def write(self, vals):
    # Si alguno de los valores que se han cambiado están en la lista de cambios que afectan al calendario
    if any([i in vals for i in self.school_calendar_update_keys]):
      vals['school_calendar_version'] = self.school_calendar_version + 1

    super(SchoolYear, self).write(vals)

    return True

  # la fecha de inicio no puede ser fin de semana
  @api.constrains('date_init')
  def _check_date_init(self):
    for record in self:
      if record.date_init.weekday() == 5 or record.date_init.weekday() == 6:
        raise ValidationError('La fecha de inicio no puede ser fin de semana')

  @api.depends('date_init')
  def _compute_name(self):
    for record in self:
      if record.date_init == False:
        record.name = ''
      else:
        record.name = '%s/%s' % (record.date_init.year, record.date_init.year + 1)

  @api.depends('date_init')
  def _compute_date_init_lective(self):
    for record in self:
      if record.date_init == False:
        record.date_init_lective = ''
      elif record.date_init.weekday() >= 2:
        record.date_init_lective = record.date_init + datetime.timedelta(days = 7 - record.date_init.weekday())
      else:
        record.date_init_lective = record.date_init

  @api.constrains('date_init_lective')
  def _check_date_init_lective(self):
    for record in self:
      if record.date_init_lective.weekday() >= 4:
        raise ValidationError('La fecha de inicio lectiva no puede ser ni viernes ni fin de semana')
  
  @api.depends('date_init_lective')
  def _compute_1term2_end(self):
    for record in self:
      if record.date_init_lective == False:
        record.date_1term2_end = ''
      else: 
        record.date_1term2_end = record.date_init_lective + datetime.timedelta(weeks=9) + datetime.timedelta(days = 4 - record.date_init_lective.weekday())

  @api.constrains('date_1term2_end')
  def _check_date_1term2_end(self):
    for record in self:
      if record.date_init.weekday() == 5 or record.date_init.weekday() == 6:
        raise ValidationError('La fecha de fin de evaluación no puede ser fin de semana')

  @api.depends('date_1term2_end','date_init_lective')    
  def _compute_duration_1term2(self):
    for record in self:
      if record.date_1term2_end != False and record.date_init_lective != False:
        record.duration_1term2 = (record.date_1term2_end - record.date_init_lective).days // 7 + 1
      else:
        record.duration_1term2 = 0
             
  @api.depends('date_1term2_end', 'holidays_ids.date')
  def _compute_1term2_exam_ini(self):
    for record in self:
      if record.date_1term2_end == False:
        record.date_1term2_exam_ini = ''
      else: 
        record.date_1term2_exam_ini = record.date_1term2_end + datetime.timedelta(days=3)

      # obtener los festivos del día de la constitucion e inmaculada
      constitucion_holiday = next((holiday for holiday in record.holidays_ids if holiday.key == 'constitucion'), None)
      inma_holiday = next((holiday for holiday in record.holidays_ids if holiday.key == 'inmaculada'), None)
   
      if constitucion_holiday == None or inma_holiday == None:
        continue
      # si en la semana de exámenes está el día 6/12 o el 8/12, retraso los exámenes una semana
      elif (constitucion_holiday.date >= record.date_1term2_exam_ini and constitucion_holiday.date < record.date_1term2_exam_end) or \
        (inma_holiday.date >= record.date_1term2_exam_ini and inma_holiday.date < record.date_1term2_exam_end):
        record.date_1term2_exam_ini = record.date_1term2_exam_ini + datetime.timedelta(weeks = 1)
        record.date_1term2_exam_end = record.date_1term2_exam_end + datetime.timedelta(weeks = 1)
        record.date_1term2_end = record.date_1term2_end + datetime.timedelta(weeks = 1)

  @api.constrains('date_1term2_exam_ini')
  def _check_date_1term2_exam_ini(self):
    for record in self:
      if record.date_1term2_exam_ini.weekday() != 0:
        raise ValidationError('La fecha de inicio de exámenes tiene que ser un lunes')
  
  @api.depends('date_1term2_exam_ini')
  def _compute_1term2_exam_end(self):
    for record in self:
      if record.date_1term2_exam_ini == False:
        record.date_1term2_exam_end = ''
      else: 
        record.date_1term2_exam_end = record.date_1term2_exam_ini + datetime.timedelta(days=4)

  @api.depends('date_init_lective')
  def _compute_welcome_day(self):
    for record in self:
      if record.date_init_lective == False:
        record.date_welcome_day = ''
      else: 
        record.date_welcome_day = record.date_init_lective - datetime.timedelta(days = 4)

  @api.depends('date_1term2_exam_end')
  def _compute_2term2_ini(self):
    for record in self:
      if record.date_1term2_exam_end == False:
        record.date_2term2_ini = ''
      else: 
        record.date_2term2_ini = record.date_1term2_exam_end + datetime.timedelta(days = 3)

  @api.depends('date_2term2_ini', 'duration_1term2')
  def _compute_2term2_end(self):
    for record in self:
      if record.date_2term2_ini == False:
        record.date_2term2_end = ''
      else:
        # 20 + 2 (ya que Navidad al final son siempre dos semanas no lectivas). 
        # Eso lo ubica al principio de la semana 21, asi que -1 y sumanos para alcanzar el viernes 
        record.date_2term2_end = record.date_2term2_ini + datetime.timedelta(weeks = 21 - record.duration_1term2) + datetime.timedelta(days = 4)
      
  @api.constrains('date_2term2_end')
  def _check_date_2term2_end(self):
    for record in self:
      if record.date_2term2_end.weekday() == 5 or record.date_2term2_end.weekday() == 6:
        raise ValidationError('La fecha de fin de evaluación no puede ser fin de semana')

  @api.depends('date_2term2_end','date_2term2_ini')    
  def _compute_duration_2term2(self):
    for record in self:
      if record.date_2term2_end != False and record.date_2term2_ini != False:
        record.duration_2term2 = (record.date_2term2_end - record.date_2term2_ini).days // 7 + 1 - 2 # - 2 por la dos de navidad 
      else:
        record.duration_2term2 = 0
             
  @api.depends('date_2term2_end')
  def _compute_2term2_exam_ini(self):
    for record in self:
      if record.date_2term2_end == False:
        record.date_2term2_exam_ini = ''
      else: 
        record.date_2term2_exam_ini = record.date_2term2_end + datetime.timedelta(days=3)

  @api.constrains('date_2term2_exam_ini')
  def _check_date_2term2_exam_ini(self):
    for record in self:
      if record.date_2term2_exam_ini != False: 
        if record.date_2term2_exam_ini.weekday() != 0:
          raise ValidationError('La fecha de inicio de exámenes tiene que ser un lunes')
  
  @api.depends('date_2term2_exam_ini')
  def _compute_2term2_exam_end(self):
    for record in self:
      if record.date_2term2_exam_ini == False:
        record.date_2term2_exam_end = ''
      else: 
        record.date_2term2_exam_end = record.date_2term2_exam_ini + datetime.timedelta(days=4)

  @api.depends('date_2term2_exam_ini')
  def _compute_ord2_exam_ini(self):
    for record in self:
      if record.date_2term2_ini == False:
        record.date_ord2_exam_ini = ''
      else: 
        record.date_ord2_exam_ini = record.date_2term2_exam_ini + datetime.timedelta(weeks = 2)

  @api.constrains('date_ord2_exam_ini')
  def _check_date_ord2_exam_ini(self):
    for record in self:
      if record.date_ord2_exam_ini != False: 
        if record.date_ord2_exam_ini.weekday() != 0:
          raise ValidationError('La fecha de inicio de exámenes tiene que ser un lunes')
  
  @api.depends('date_2term2_exam_ini')
  def _compute_ord2_exam_end(self):
    for record in self:
      if record.date_ord2_exam_ini == False:
        record.date_ord2_exam_end = ''
      else: 
        record.date_ord2_exam_end = record.date_ord2_exam_ini + datetime.timedelta(days=4)
  
  @api.depends('date_ord2_exam_ini')
  def _compute_cancellation2(self):
    for record in self:
      christmas_holiday = next((holiday for holiday in record.holidays_ids if holiday.key == 'navidad'), None)

      _logger.info(christmas_holiday)
      
      if record.date_ord2_exam_ini == False:
        record.date_cancellation2 = ''
      else: 
        record.date_cancellation2 = datetime.datetime(record.date_ord2_exam_ini.year, 1, record.date_ord2_exam_ini.day)
        if christmas_holiday == None:
          continue
        elif (record.date_cancellation2 >= christmas_holiday.date and record.date_cancellation2 <= christmas_holiday.date_end):
          record.date_cancellation2 = christmas_holiday.date_end + datetime.timedelta(days = 1)
        

  @api.depends('date_ord2_exam_ini')
  def _compute_waiver_ord2(self):
    for record in self:
      if record.date_ord2_exam_ini == False:
        record.date_waiver_ord2 = ''      
      else:
        record.date_waiver_ord2 = datetime.datetime(record.date_ord2_exam_ini.year, record.date_ord2_exam_ini.month - 1, record.date_ord2_exam_ini.day)

  @api.depends('date_extraord2_exam_ini')
  def _compute_waiver_extraord2(self):
    for record in self:
      record.date_waiver_extraord2 = ''
    pass
    """  for record in self:
      if record.date_ord2_exam_ini == False:
        record.date_waiver_extraord2 = ''      
      else:
        record.date_waiver_extraord2 = datetime.datetime(record.date_extraord2_exam_ini.year, record.date_extraord2_exam_ini.month - 1, record.date_extraord2_exam_ini.day) """

  @api.onchange('date_init')
  def _calculate_holidays(self):
    if self._origin.date_init == False:
      return
    
    for record in self:
      # si el año anterior es igual al que se acaba de cambiar no se hace nada
      if self._origin.date_init.year == record.date_init.year:
        continue

      # fiestas de navidad
      date_christmas_holidayI = datetime.datetime(record.date_init.year, 12, 23) # de partida es el 23/12
   
      if date_christmas_holidayI.weekday() == 0: # cae lunes
        date_christmas_holidayI = datetime.datetime(record.date_init.year, 12, 21)
      elif date_christmas_holidayI.weekday() == 1:  # cae martes
        date_christmas_holidayI = datetime.datetime(record.date_init.year, 12, 20)
      elif date_christmas_holidayI.weekday() == 6: # cae domingo
        date_christmas_holidayI = datetime.datetime(record.date_init.year, 12, 22)

      date_christmas_holidayE = datetime.datetime(record.date_init.year + 1, 1, 6) # de partida es el 6/1
      if date_christmas_holidayE.weekday() >= 3 and date_christmas_holidayE.weekday() <= 5:
        date_christmas_holidayE = date_christmas_holidayE + datetime.timedelta(days = 6 - date_christmas_holidayE.weekday())

      # fallas
      date_fallas_holidayI = datetime.datetime(record.date_init.year + 1, 3, 15) # de partida es el 15/3
      if date_fallas_holidayI.weekday() == 0: # cae lunes
        date_fallas_holidayI = datetime.datetime(record.date_init.year, 3, 12)
      elif date_fallas_holidayI.weekday() == 1:  # cae martes
        date_fallas_holidayI = datetime.datetime(record.date_init.year + 1, 3, 20)
      elif date_fallas_holidayI.weekday() == 6: # cae domingo
        date_fallas_holidayI = datetime.datetime(record.date_init.year + 1, 3, 14)

      date_fallas_holidayE = datetime.datetime(record.date_init.year + 1, 3, 19) # de partida es el 19/3
      if date_fallas_holidayE.weekday() >= 3 and date_fallas_holidayE.weekday() <= 5:
        date_fallas_holidayE = date_fallas_holidayE + datetime.timedelta(days = 6 - date_fallas_holidayE.weekday())

      # elimino todos los registros "en el aire", pero se recuperan en el caso de que se cancele la modificación
      # del school_year
      record.holidays_ids = [(5, 0 ,0)]
      # añade nuevos registro, pero los mantiene en "el aire" hasta que se grabe el school_year
      record.holidays_ids = [(0, 0, {
        'school_year_id': self._origin.id,
        'description': 'Día Comunidad Valenciana', 
        'date': datetime.datetime(record.date_init.year, 10, 9), 
        'date_end': datetime.datetime(record.date_init.year, 10, 9) }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': 'Día Hispanidad', 
        'date': datetime.datetime(record.date_init.year, 10, 12), 
        'date_end': datetime.datetime(record.date_init.year, 10, 12) }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': 'Todos los santos', 
        'date': datetime.datetime(record.date_init.year, 11, 1), 
        'date_end': datetime.datetime(record.date_init.year, 11, 1) }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': 'Constitución', 
        'date': datetime.datetime(record.date_init.year, 12, 6), 
        'date_end': datetime.datetime(record.date_init.year, 12, 6),
        'key': 'constitucion' }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': 'Inmaculada', 
        'date': datetime.datetime(record.date_init.year, 12, 8), 
        'date_end': datetime.datetime(record.date_init.year, 12, 8),
        'key': 'inmaculada' }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': 'Navidades', 
        'date': date_christmas_holidayI,
        'date_end': date_christmas_holidayE,
        'key': 'navidad' }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': 'San Vicente Martir', 
        'date': datetime.datetime(record.date_init.year + 1, 1, 22), 
        'date_end': datetime.datetime(record.date_init.year + 1, 1, 22) }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': 'Fallas', 
        'date': date_fallas_holidayI,
        'date_end': date_fallas_holidayE }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': 'Pascuas', 
        'date': self._calc_easter(record.date_init.year + 1) + datetime.timedelta(days = -3),
        'date_end': self._calc_easter(record.date_init.year + 1) + datetime.timedelta(days = 8) }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': '1º Mayo', 
        'date': datetime.datetime(record.date_init.year + 1, 5, 1), 
        'date_end': datetime.datetime(record.date_init.year + 1, 5, 1) })
        ]  

  """
  https://www.daniweb.com/programming/software-development/code/463551/another-look-at-easter-dates-python
  """
  @staticmethod
  def _calc_easter(year):
    '''
    Gauss algorithm to calculate the date of easter in a given year
    note // forces integer division in Python3
    returns a date object
    '''
    month = 3
    # determine the Golden number
    golden = (year % 19) + 1
    # determine the century number
    century = year // 100 + 1
    # correct for the years who are not leap years
    xx = (3 * century) // 4 - 12
    # moon correction
    yy = (8 * century + 5) // 25 - 5
    # find Sunday
    zz = (5 * year) // 4 - xx - 10
    # determine epact
    # age of moon on January 1st of that year
    # (follows a cycle of 19 years)
    ee = (11 * golden + 20 + yy - xx) % 30
    if ee == 24:
      ee += 1
    if ee == 25 and golden > 11:
      ee += 1
    # get the full moon
    moon = 44 - ee
    if moon < 21:
      moon += 30
    # up to Sunday
    day = (moon + 7) - ((zz + moon) % 7)
    # possibly up a month in easter_date
    if day > 31:
      day -= 31
      month = 4

    return datetime.datetime(year, month, day)

  "Calcula los dias entre dos fechas, pero si cambia de mes, sólo hasta final o principio de ese mes"
  def _calc_dur(dateI, dateE):
    if dateI.month == dateE.month:
      return (dateE-dateI).days
    else:
      if dateI < dateE:
        return (datetime.datetime(dateI.year, dateI.month, 31) - dateI).days + 1
      else:
        return (datetime.datetime(dateI.year, dateI.month, 1) - dateI).days - 1
      


  def update_dates(self):
    self.dates['init_lective'] = { 
      'date': self.date_init_lective,
      'desc': self._fields['date_init_lective'].string, 
      'type': 'G'
    }

    self.dates['1term2_end'] = { 
      'date': self.date_1term2_end,
      'desc': self._fields['date_1term2_end'].string, 
      'type': 'S'
    }

    self.dates['date_1term2_exam_ini'] = { 
      'date': self.date_1term2_exam_ini,
      'desc': self._fields['date_1term2_exam_ini'].string, 
      'type': 'S',
      # días que dura este evento, además del día indicado
      'dur': self.date_1term2_exam_end - self.date_1term2_exam_ini
    }

    self.dates['date_1term2_exam_end'] = { 
      'date': self.date_1term2_exam_end,
      'desc': self._fields['date_1term2_exam_end'].string, 
      'type': 'S',
      'dur': self.date_1term2_exam_ini - self.date_1term2_exam_end,
    }

    self.dates['date_welcome_day'] = { 
      'date': self.date_welcome_day, 
      'desc': self._fields['date_welcome_day'].string,
      'type': 'G'
    }
    
    self.dates['date_2term2_ini'] = { 
      'date': self.date_2term2_ini,
      'desc': self._fields['date_2term2_ini'].string, 
      'type': 'S',
    }

    self.dates['date_2term2_end'] = { 
      'date': self.date_2term2_end,
      'desc': self._fields['date_2term2_end'].string, 
      'type': 'S',
    }

    self.dates['date_2term2_exam_ini'] = { 
      'date': self.date_2term2_exam_ini,
      'desc': self._fields['date_2term2_exam_ini'].string, 
      'type': 'S',
      'dur': self.date_2term2_exam_end - self.date_2term2_exam_ini
    }

    self.dates['date_2term2_exam_end'] = { 
      'date': self.date_2term2_exam_end,
      'desc': self._fields['date_2term2_exam_end'].string, 
      'type': 'S',
      'dur': self.date_2term2_exam_ini - self.date_2term2_exam_end,
    }

    self.dates['date_ord2_exam_ini'] = { 
      'date': self.date_ord2_exam_ini,
      'desc': self._fields['date_ord2_exam_ini'].string, 
      'type': 'S',
      'dur': self.date_ord2_exam_end - self.date_ord2_exam_ini,
    }

    self.dates['date_ord2_exam_end'] = { 
      'date': self.date_ord2_exam_end,
      'desc': self._fields['date_ord2_exam_end'].string, 
      'type': 'S',
      'dur': self.date_ord2_exam_ini - self.date_ord2_exam_end,
    }

    self.dates['date_extraord2_exam_ini'] = { 
      'date': self.date_extraord2_exam_ini,
      'desc': self._fields['date_extraord2_exam_ini'].string, 
      'type': 'S',
      'dur': self.date_extraord2_exam_end - self.date_extraord2_exam_ini,
    }

    self.dates['date_extraord2_exam_end'] = { 
      'date': self.date_extraord2_exam_end,
      'desc': self._fields['date_extraord2_exam_end'].string, 
      'type': 'S',
      'dur': self.date_extraord2_exam_ini - self.date_extraord2_exam_end,
    }
    
    self.dates['date_cancellation2'] = { 
      'date': self.date_cancellation2,
      'desc': self._fields['date_cancellation2'].string, 
      'type': 'S',
    }
  
    self.dates['date_waiver_ord2'] = { 
      'date': self.date_waiver_ord2,
      'desc': self._fields['date_waiver_ord2'].string, 
      'type': 'S',
    }
  
    self.dates['date_waiver_extraord2'] = { 
      'date': self.date_waiver_extraord2,
      'desc': self._fields['date_waiver_extraord2'].string, 
      'type': 'S',
    }
