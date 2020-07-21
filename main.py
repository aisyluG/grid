from autoSettings import autoSettings
import pandas as pd
file = 'D:/ucheba/python/grid/10.txt'
settings = autoSettings()
#получение рекомендованных настроек
ss = settings.get_auto_settings(file)
# проверка настроек
print(settings.check_settings(file, ss))


















