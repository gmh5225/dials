from __future__ import division

from export_mtz import sum_partial_reflections
from export_mtz import scale_partial_reflections

def export_xds_ascii(integrated_data, experiment_list, hklout, summation=False,
                     include_partials=False, keep_partials=False):
  '''Export data from integrated_data corresponding to experiment_list to
  an XDS_ASCII.HKL formatted text file.'''

  from logging import info
  from dials.array_family import flex
  import math

  # for the moment assume (and assert) that we will convert data from exactly
  # one lattice...

  assert(len(experiment_list) == 1)
  # select reflections that are assigned to an experiment (i.e. non-negative id)

  integrated_data = integrated_data.select(integrated_data['id'] >= 0)
  assert max(integrated_data['id']) == 0

  if not summation:
    assert('intensity.prf.value' in integrated_data)

  if 'intensity.prf.variance' in integrated_data:
    selection = integrated_data.get_flags(
      integrated_data.flags.integrated,
      all=True)
  else:
    selection = integrated_data.get_flags(
      integrated_data.flags.integrated_sum)
  integrated_data = integrated_data.select(selection)

  selection = integrated_data['intensity.sum.variance'] <= 0
  if selection.count(True) > 0:
    integrated_data.del_selected(selection)
    info('Removing %d reflections with negative variance' % \
          selection.count(True))

  if 'intensity.prf.variance' in integrated_data:
    selection = integrated_data['intensity.prf.variance'] <= 0
    if selection.count(True) > 0:
      integrated_data.del_selected(selection)
      info('Removing %d profile reflections with negative variance' % \
            selection.count(True))

  if include_partials:
    integrated_data = sum_partial_reflections(integrated_data)
    integrated_data = scale_partial_reflections(integrated_data)

  if 'partiality' in integrated_data:
    selection = integrated_data['partiality'] < 0.99
    if selection.count(True) > 0 and not keep_partials:
      integrated_data.del_selected(selection)
      info('Removing %d incomplete reflections' % \
        selection.count(True))

  experiment = experiment_list[0]

  # sort data before output
  nref = len(integrated_data['miller_index'])
  indices = flex.size_t_range(nref)
  perm = sorted(indices, key=lambda k: integrated_data['miller_index'][k])
  integrated_data = integrated_data.select(flex.size_t(perm))

  from scitbx import matrix

  assert (not experiment.goniometer is None)

  unit_cell = experiment.crystal.get_unit_cell()

  from scitbx.array_family import flex
  from math import floor, sqrt

  assert(not experiment.scan is None)
  image_range = experiment.scan.get_image_range()
  phi_start, phi_range = experiment.scan.get_image_oscillation(image_range[0])

  UB = matrix.sqr(experiment.crystal.get_A())
  real_space_ABC = UB.inverse().elems

  # gather the required information for the reflection file

  nref = len(integrated_data['miller_index'])
  zdet = flex.double(integrated_data['xyzcal.px'].parts()[2])

  miller_index = integrated_data['miller_index']

  I = None
  sigI = None

  # export including scale factors

  if 'lp' in integrated_data:
    lp = integrated_data['lp']
  else:
    lp = flex.double(nref, 1.0)
  if 'dqe' in integrated_data:
    dqe = integrated_data['dqe']
  else:
    dqe = flex.double(nref, 1.0)
  scl = lp / dqe

  var_model = 4.0, 1e-4

  if summation:
    I = integrated_data['intensity.sum.value'] * scl
    V = integrated_data['intensity.sum.variance'] * scl * scl
    assert V.all_gt(0)
    V = var_model[0] * (V + var_model[1] * I * I)
    sigI = flex.sqrt(V)
  else:
    I = integrated_data['intensity.prf.value'] * scl
    V = integrated_data['intensity.prf.variance'] * scl * scl
    assert V.all_gt(0)
    V = var_model[0] * (V + var_model[1] * I * I)
    sigI = flex.sqrt(V)

  fout = open(hklout, 'w')

  # first write the header

  panel = experiment.detector[0]
  qx, qy = panel.get_pixel_size()
  nx, ny = panel.get_image_size()
  distance = matrix.col(panel.get_origin()).dot(
      matrix.col(panel.get_normal()))
  org = matrix.col(panel.get_origin()) - distance * matrix.col(
      panel.get_normal())
  orgx = - org.dot(matrix.col(panel.get_fast_axis())) / qx
  orgy = - org.dot(matrix.col(panel.get_slow_axis())) / qy

  fout.write('\n'.join([
    '!FORMAT=XDS_ASCII    MERGE=FALSE    FRIEDEL\'S_LAW=FALSE',
    '!Generated by dials.export',
    '!DATA_RANGE= %d %d' % image_range,
    '!ROTATION_AXIS= %f %f %f' % experiment.goniometer.get_rotation_axis(),
    '!OSCILLATION_RANGE= %f' % phi_range,
    '!START_ANGLE= %f' % phi_start,
    '!START_FRAME= %d' % image_range[0],
    '!SPACE_GROUP_NUMBER= %d' % experiment.crystal.get_space_group().type().number(),
    '!UNIT_CELL_CONSTANTS= %f %f %f %f %f %f' % unit_cell.parameters(),
    '!UNIT_CELL_A-AXIS= %f %f %f' % real_space_ABC[0:3],
    '!UNIT_CELL_B-AXIS= %f %f %f' % real_space_ABC[3:6],
    '!UNIT_CELL_C-AXIS= %f %f %f' % real_space_ABC[6:9],
    '!X-RAY_WAVELENGTH= %f' % experiment.beam.get_wavelength(),
    '!INCIDENT_BEAM_DIRECTION= %f %f %f' % experiment.beam.get_s0(),
    '!NX= %d NY= %d QX= %f QY= %f' % (nx, ny, qx, qy),
    '!ORGX= %f ORGY= %f' % (orgx, orgy),
    '!DETECTOR_DISTANCE= %f' % distance,
    '!DIRECTION_OF_DETECTOR_X-AXIS= %f %f %f' % panel.get_fast_axis(),
    '!DIRECTION_OF_DETECTOR_Y-AXIS= %f %f %f' % panel.get_slow_axis(),
    '!VARIANCE_MODEL= %f %f' % var_model,
    '!NUMBER_OF_ITEMS_IN_EACH_DATA_RECORD=12',
    '!ITEM_H=1',
    '!ITEM_K=2',
    '!ITEM_L=3',
    '!ITEM_IOBS=4',
    '!ITEM_SIGMA(IOBS)=5',
    '!ITEM_XD=6',
    '!ITEM_YD=7',
    '!ITEM_ZD=8',
    '!ITEM_RLP=9',
    '!ITEM_PEAK=10',
    '!ITEM_CORR=11',
    '!ITEM_PSI=12',
    '!END_OF_HEADER']))

  # then write the data records

  beam = matrix.col(experiment.beam.get_direction())

  s0 = matrix.col(experiment.beam.get_s0())

  for j in range(nref):
    h, k, l = miller_index[j]
    x = UB * (h, k, l)
    s = s0 + x
    g = s0.cross(s).normalize()
    f = (UB * (h, k, l)).normalize()

    # find component of beam perpendicular to f, e
    e = (beam - (beam.dot(f) * f)).normalize()
    if h == k and k == l:
      u = (h, -h, 0)
    else:
      u = (k - l, l - h, h - k)
    q = (matrix.col(u).transpose() * UB.inverse()).normalize()

    psi = q.angle(g, deg=True)
    if q.dot(e) < 0:
      psi *= -1

    x, y, z = integrated_data['xyzcal.px'][j]

    fout.write('%d %d %d %f %f %f %f %f %f 100 100 %f\n' %
               (h, k, l, I[j], sigI[j], x, y, z, lp[j], psi))
  fout.close()
  info('Output %d reflections to %s' % (nref, hklout))
  return
