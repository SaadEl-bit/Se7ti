-- FieldScreen AI v2 — Mock seed data for development

INSERT INTO pharmacies (id, name, address, phone, latitude, longitude) VALUES
  ('a1000000-0000-0000-0000-000000000001', 'Pharmacie Centrale Oujda', '25 Av. Mohammed V, Oujda', '+212 636-000001', 34.686, -1.911),
  ('a1000000-0000-0000-0000-000000000002', 'Pharmacie Al Amal', '12 Rue Berkane, Oujda', '+212 636-000002', 34.679, -1.903),
  ('a1000000-0000-0000-0000-000000000003', 'Pharmacie Ibn Sina', '7 Bd Hassan II, Oujda', '+212 636-000003', 34.691, -1.920),
  ('a1000000-0000-0000-0000-000000000004', 'Pharmacie Salam', '3 Av. Bir Anzarane, Oujda', '+212 636-000004', 34.675, -1.898),
  ('a1000000-0000-0000-0000-000000000005', 'Pharmacie Nour', '88 Rue Al Qods, Oujda', '+212 636-000005', 34.682, -1.930);

INSERT INTO garde_calendar (pharmacy_id, date, heure_debut, heure_fin) VALUES
  ('a1000000-0000-0000-0000-000000000001', CURRENT_DATE, '08:00', '22:00'),
  ('a1000000-0000-0000-0000-000000000003', CURRENT_DATE, '22:00', '08:00');

INSERT INTO users (id, email, pseudo, phone, latitude, longitude, pathologies) VALUES
  ('b1000000-0000-0000-0000-000000000001', 'patient_a@example.com', 'PatientA', '+212 661-000001', 34.678, -1.905, ARRAY['diabete_type2']),
  ('b1000000-0000-0000-0000-000000000002', 'patient_b@example.com', 'PatientB', '+212 661-000002', 34.683, -1.908, ARRAY['hta']),
  ('b1000000-0000-0000-0000-000000000003', 'patient_c@example.com', 'PatientC', '+212 661-000003', 34.671, -1.915, ARRAY['diabete_type2', 'hta']),
  ('b1000000-0000-0000-0000-000000000004', 'patient_d@example.com', 'PatientD', '+212 661-000004', 34.692, -1.900, ARRAY['asthme']),
  ('b1000000-0000-0000-0000-000000000005', 'patient_e@example.com', 'PatientE', '+212 661-000005', 34.688, -1.922, ARRAY['insuffisance_renale']);

INSERT INTO medications (user_id, name, dosage, stock_quantity, stock_unit, alert_threshold) VALUES
  ('b1000000-0000-0000-0000-000000000001', 'Metformine', '500mg', 15, 'comprime', 7),
  ('b1000000-0000-0000-0000-000000000001', 'Glibenclamide', '5mg', 4, 'comprime', 7),
  ('b1000000-0000-0000-0000-000000000002', 'Amlodipine', '10mg', 20, 'comprime', 7),
  ('b1000000-0000-0000-0000-000000000002', 'Losartan', '50mg', 10, 'comprime', 7),
  ('b1000000-0000-0000-0000-000000000003', 'Metformine', '850mg', 30, 'comprime', 7),
  ('b1000000-0000-0000-0000-000000000003', 'Enalapril', '10mg', 3, 'comprime', 7),
  ('b1000000-0000-0000-0000-000000000004', 'Salbutamol', '100mcg', 2, 'bouffee', 5),
  ('b1000000-0000-0000-0000-000000000004', 'Budesonide', '200mcg', 8, 'bouffee', 5),
  ('b1000000-0000-0000-0000-000000000005', 'Furosemide', '40mg', 25, 'comprime', 7);
