const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

// Veritabanı dosya yolu
const DB_PATH = path.join(process.cwd(), '..', 'data', 'campaigns.db');
const SCHEMA_PATH = path.join(process.cwd(), '..', 'scraper', 'schema.sql');

// Veritabanı bağlantısı (singleton pattern)
let db = null;

function getDatabase() {
  if (db) {
    return db;
  }

  // Veritabanı dosyasının olup olmadığını kontrol et
  const dbExists = fs.existsSync(DB_PATH);

  // Veritabanı bağlantısını oluştur
  db = new Database(DB_PATH, {
    verbose: process.env.NODE_ENV === 'development' ? console.log : null,
  });

  // Eğer veritabanı yoksa veya boşsa, şemayı oluştur
  if (!dbExists) {
    console.log('Creating database schema...');
    const schema = fs.readFileSync(SCHEMA_PATH, 'utf-8');
    db.exec(schema);
    console.log('Database schema created successfully.');
  }

  // WAL mode'u aktifleştir (daha iyi performans)
  db.pragma('journal_mode = WAL');

  return db;
}

// Veritabanı bağlantısını kapat
function closeDatabase() {
  if (db) {
    db.close();
    db = null;
  }
}

module.exports = {
  getDatabase,
  closeDatabase,
};
