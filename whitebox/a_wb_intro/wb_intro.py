import whitebox_workflows as wbw
from whitebox_workflows import WbEnvironment

wbe = WbEnvironment()

wbe.working_directory = wbw.download_sample_data('Guelph_landsat')
print(f'Data have been stored in: {wbe.working_directory}')

