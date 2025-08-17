PRAGMA journal_mode=WAL;

CREATE TABLE modes (id INTEGER PRIMARY KEY CHECK(id=1), active TEXT NOT NULL DEFAULT 'reverse');
INSERT INTO modes(id, active) VALUES(1, 'reverse');

CREATE TABLE reversing_settings (
  id INTEGER PRIMARY KEY CHECK(id=1),
  min_distance_m REAL DEFAULT 0.5,
  max_distance_m REAL DEFAULT 5.0,
  f_min_hz REAL DEFAULT 0.1,
  f_max_hz REAL DEFAULT 10.0,
  resolution TEXT DEFAULT '1280x720',
  fps INTEGER DEFAULT 30,
  rotation INTEGER DEFAULT 90,
  overlay_pos TEXT DEFAULT 'bottom-right',
  overlay_scale REAL DEFAULT 1.0,
  transpose_dir INTEGER DEFAULT 1
);
INSERT INTO reversing_settings(id) VALUES(1);

CREATE TABLE surveillance_settings (
  id INTEGER PRIMARY KEY CHECK(id=1),
  preroll_sec INTEGER DEFAULT 5,
  clip_len_sec INTEGER DEFAULT 300,
  resolution TEXT DEFAULT '1280x720',
  rotation INTEGER DEFAULT 90,
  sensitivity INTEGER DEFAULT 60,
  flash_ms INTEGER DEFAULT 250,
  light_during_record INTEGER DEFAULT 1,
  overlay TEXT DEFAULT 'date,time,cam',
  overlay_scale REAL DEFAULT 1.0,
  retention_days INTEGER DEFAULT 14,
  transpose_dir INTEGER DEFAULT 1
);
INSERT INTO surveillance_settings(id) VALUES(1);

CREATE TABLE led_settings (
  id INTEGER PRIMARY KEY CHECK(id=1),
  master_enabled INTEGER DEFAULT 1,
  brightness INTEGER DEFAULT 128,
  color_white TEXT DEFAULT '#FFFFFF',
  color_red   TEXT DEFAULT '#FF0000',
  lux_rev_on INTEGER DEFAULT 20,
  lux_surv_on INTEGER DEFAULT 20,
  anim_profile TEXT DEFAULT 'alt_warn'
);
INSERT INTO led_settings(id) VALUES(1);

CREATE TABLE system_settings (
  id INTEGER PRIMARY KEY CHECK(id=1),
  shutdown_voltage REAL DEFAULT 3.3,
  tz TEXT DEFAULT 'Europe/London',
  log_level TEXT DEFAULT 'INFO'
);
INSERT INTO system_settings(id) VALUES(1);

CREATE TABLE events (
  id TEXT PRIMARY KEY,
  ts_start TEXT,
  ts_end TEXT,
  path TEXT,
  motion_score REAL
);
