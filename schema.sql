PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS modes (
  id INTEGER PRIMARY KEY CHECK(id=1),
  active TEXT NOT NULL DEFAULT 'reverse'
);
INSERT OR IGNORE INTO modes(id, active) VALUES (1,'reverse');

CREATE TABLE IF NOT EXISTS reversing_settings (
  id INTEGER PRIMARY KEY CHECK(id=1),
  min_distance REAL NOT NULL DEFAULT 0.3,
  max_distance REAL NOT NULL DEFAULT 5.0,
  led_warn_min_hz REAL NOT NULL DEFAULT 0.1,
  led_warn_max_hz REAL NOT NULL DEFAULT 10.0,
  resolution TEXT NOT NULL DEFAULT '1280x720',
  framerate INTEGER NOT NULL DEFAULT 30,
  rotation INTEGER NOT NULL DEFAULT 0,
  overlay_pos TEXT NOT NULL DEFAULT 'br'
);
INSERT OR IGNORE INTO reversing_settings(id) VALUES (1);

CREATE TABLE IF NOT EXISTS surveillance_settings (
  id INTEGER PRIMARY KEY CHECK(id=1),
  preroll_sec INTEGER NOT NULL DEFAULT 5,
  record_len_sec INTEGER NOT NULL DEFAULT 300,
  resolution TEXT NOT NULL DEFAULT '1280x720',
  rotation INTEGER NOT NULL DEFAULT 0,
  motion_sensitivity INTEGER NOT NULL DEFAULT 5,
  led_motion_flash_sec INTEGER NOT NULL DEFAULT 1,
  led_lighting_enabled INTEGER NOT NULL DEFAULT 0,
  overlay TEXT NOT NULL DEFAULT 'date,time,camera'
);
INSERT OR IGNORE INTO surveillance_settings(id) VALUES (1);

CREATE TABLE IF NOT EXISTS led_settings (
  id INTEGER PRIMARY KEY CHECK(id=1),
  master_enabled INTEGER NOT NULL DEFAULT 0,
  brightness INTEGER NOT NULL DEFAULT 64,
  color_white TEXT NOT NULL DEFAULT '#FFFFFF',
  color_red   TEXT NOT NULL DEFAULT '#FF0000'
);
INSERT OR IGNORE INTO led_settings(id) VALUES (1);

CREATE TABLE IF NOT EXISTS system_settings (
  id INTEGER PRIMARY KEY CHECK(id=1),
  shutdown_enabled INTEGER NOT NULL DEFAULT 0,
  shutdown_voltage REAL NOT NULL DEFAULT 3.3
);
INSERT OR IGNORE INTO system_settings(id) VALUES (1);

CREATE TABLE IF NOT EXISTS events (
  id TEXT PRIMARY KEY,
  ts_start TEXT, ts_end TEXT, type TEXT, meta TEXT
);
