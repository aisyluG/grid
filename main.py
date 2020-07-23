from autoSettings import autoSettings
import pandas as pd
file = 'D:/ucheba/python/grid/datasets/09_0_з_м_д_м_(sep=табуляция)(decimal=запятая).txt'
settings = autoSettings()
#получение рекомендованных настроек
ss = settings.get_auto_settings(file)
# проверка настроек
print(settings.check_settings(file, ss))
print(ss)
print(settings.get_data(file))

















