PRAGMA foreign_keys = ON;
BEGIN;

-- Track applied migrations (optional, useful for future ALTERs)
CREATE TABLE IF NOT EXISTS _migrations (
  id TEXT PRIMARY KEY,
  applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- Core config tables (all singleton rows with id=1)
-- ============================================================

CREATE TABLE IF NOT EXISTS modes (
  id      INTEGER PRIMARY KEY CHECK (id = 1),
  active  TEXT NOT NULL CHECK (active IN ('reverse','surveillance'))
);
-- Seed only if empty
INSERT INTO modes (id, active)
SELECT 1, 'reverse'
WHERE NOT EXISTS (SELECT 1 FROM modes WHERE id = 1);

-- Reversing (low-latency) settings
CREATE TABLE IF NOT EXISTS reversing_settings (
  id               INTEGER PRIMARY KEY CHECK (id = 1),
  min_distance_m   REAL NOT NULL DEFAULT 0.4,
  max_distance_m   REAL NOT NULL DEFAULT 3.0,
  f_min_hz         REAL NOT NULL DEFAULT 0.1,  -- LED blink low
  f_max_hz         REAL NOT NULL DEFAULT 10.0, -- LED blink high
  resolution       TEXT NOT NULL DEFAULT '1280x720',
  fps              INTEGER NOT NULL DEFAULT 30,
  rotation         INTEGER NOT NULL DEFAULT 0 CHECK (rotation IN (0,90,180,270)),
  transpose_dir    INTEGER NOT NULL DEFAULT 1 CHECK (transpose_dir IN (0,1,2,3)),
  overlay_pos      TEXT NOT NULL DEFAULT 'bottom-right',
  overlay_scale    REAL NOT NULL DEFAULT 1.0,
  overlay_offset_m REAL NOT NULL DEFAULT 0.0
);
INSERT INTO reversing_settings (id,min_distance_m,max_distance_m,f_min_hz,f_max_hz,resolution,fps,rotation,transpose_dir,overlay_pos,overlay_scale,overlay_offset_m)
SELECT 1,0.4,3.0,0.1,10.0,'1280x720',30,0,1,'bottom-right',1.0,0.0
WHERE NOT EXISTS (SELECT 1 FROM reversing_settings WHERE id = 1);

-- Surveillance (recording) settings
CREATE TABLE IF NOT EXISTS surveillance_settings (
  id                     INTEGER PRIMARY KEY CHECK (id = 1),
  preroll_s              INTEGER NOT NULL DEFAULT 5,
  clip_len_s             INTEGER NOT NULL DEFAULT 300,
  resolution             TEXT NOT NULL DEFAULT '1280x720',
  fps                    INTEGER NOT NULL DEFAULT 24,
  rotation               INTEGER NOT NULL DEFAULT 0 CHECK (rotation IN (0,90,180,270)),
  transpose_dir          INTEGER NOT NULL DEFAULT 1 CHECK (transpose_dir IN (0,1,2,3)),
  sensitivity            REAL NOT NULL DEFAULT 0.6 CHECK (sensitivity >= 0.0 AND sensitivity <= 1.0),
  led_motion_flash_s     INTEGER NOT NULL DEFAULT 1,
  led_lighting_enabled   INTEGER NOT NULL DEFAULT 0, -- 0/1
  overlay_text           TEXT     DEFAULT 'CAM',
  overlay_pos            TEXT NOT NULL DEFAULT 'bottom-right',
  overlay_scale          REAL NOT NULL DEFAULT 1.0,
  retention_days         INTEGER NOT NULL DEFAULT 7
);
INSERT INTO surveillance_settings (id,preroll_s,clip_len_s,resolution,fps,rotation,transpose_dir,sensitivity,led_motion_flash_s,led_lighting_enabled,overlay_text,overlay_pos,overlay_scale,retention_days)
SELECT 1,5,300,'1280x720',24,0,1,0.6,1,0,'CAM','bottom-right',1.0,7
WHERE NOT EXISTS (SELECT 1 FROM surveillance_settings WHERE id = 1);

-- LED ring settings
CREATE TABLE IF NOT EXISTS led_settings (
  id                INTEGER PRIMARY KEY CHECK (id = 1),
  master_enabled    INTEGER NOT NULL DEFAULT 1,  -- 0/1
  brightness        INTEGER NOT NULL DEFAULT 64, -- 0..255
  lux_reverse_on    REAL    NOT NULL DEFAULT 15.0,
  lux_surv_on       REAL    NOT NULL DEFAULT 15.0,
  color_white       TEXT    NOT NULL DEFAULT '#FFFFFF',
  color_red         TEXT    NOT NULL DEFAULT '#FF0000',
  animation         TEXT    NOT NULL DEFAULT 'none'
);
INSERT INTO led_settings (id,master_enabled,brightness,lux_reverse_on,lux_surv_on,color_white,color_red,animation)
SELECT 1,1,64,15.0,15.0,'#FFFFFF','#FF0000','none'
WHERE NOT EXISTS (SELECT 1 FROM led_settings WHERE id = 1);

-- System settings
CREATE TABLE IF NOT EXISTS system_settings (
  id                 INTEGER PRIMARY KEY CHECK (id = 1),
  shutdown_voltage   REAL NOT NULL DEFAULT 3.30,
  wifi_timeout_s     INTEGER NOT NULL DEFAULT 30,
  ap_ssid            TEXT NOT NULL DEFAULT 'MotionPiCam-AP',
  ap_psk             TEXT NOT NULL DEFAULT 'changeMe123',
  dark_mode          INTEGER NOT NULL DEFAULT 1   -- 0/1
);
INSERT INTO system_settings (id,shutdown_voltage,wifi_timeout_s,ap_ssid,ap_psk,dark_mode)
SELECT 1,3.30,30,'MotionPiCam-AP','changeMe123',1
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE id = 1);

-- ============================================================
-- Events (many rows)
-- ============================================================
CREATE TABLE IF NOT EXISTS events (
  id        TEXT PRIMARY KEY,       -- ULID/UUID
  ts_start  TEXT,                   -- ISO8601
  ts_end    TEXT,
  kind      TEXT,                   -- 'motion','manual','schedule'
  meta_json TEXT                    -- optional JSON blob
);

-- Helpful indexes (CREATE IF NOT EXISTS supported in SQLite 3.8.0+)
CREATE INDEX IF NOT EXISTS idx_events_ts_start ON events (ts_start);
CREATE INDEX IF NOT EXISTS idx_events_kind     ON events (kind);

-- Mark migration applied (idempotent)
INSERT OR IGNORE INTO _migrations (id) VALUES ('001_init_idempotent');

COMMIT;
