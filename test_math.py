import numpy as np

# Simulate a 3 dB loss cable
raw_s21 = 15.0 # Measured S21 is 15 dB
cable_s21 = -3.0 # Cable has 3 dB loss

# get_calibration_loss logic:
loss_db = -cable_s21 # loss_db = -(-3) = 3
total_loss_db = loss_db

# plotS21 logic:
s21_corr = raw_s21 + total_loss_db # 15 + 3 = 18

print(f"S21 Math: raw={raw_s21}, cable_s21={cable_s21} -> s21_corr={s21_corr}")

# Simulate Noise Power with 3 dB loss cable
raw_np = -110.0 # Measured NP
cable_s21 = -3.0
loss_db = -cable_s21 # 3
total_loss_db = loss_db

# plotNPD logic:
np_corr = raw_np + total_loss_db # -110 + 3 = -107

print(f"NP Math: raw={raw_np}, cable_s21={cable_s21} -> np_corr={np_corr}")
