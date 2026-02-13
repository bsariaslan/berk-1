'use client';

import { useState, useEffect } from 'react';
import styles from './BankSelector.module.css';

export default function BankSelector({ onBanksChange }) {
  const [banks, setBanks] = useState([]);
  const [selectedBanks, setSelectedBanks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBanks();
  }, []);

  const fetchBanks = async () => {
    try {
      const response = await fetch('/api/banks');
      const data = await response.json();
      if (data.success) {
        setBanks(data.data);
      }
    } catch (error) {
      console.error('Bankalar yüklenemedi:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleBank = (bankId) => {
    setSelectedBanks(prev => {
      const newSelection = prev.includes(bankId)
        ? prev.filter(id => id !== bankId)
        : [...prev, bankId];

      onBanksChange(newSelection);
      return newSelection;
    });
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className="spinner"></div>
        <p className="text-muted">Bankalar yükleniyor...</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <h2 className="heading-3">Bankalarınızı Seçin</h2>
      <div className={styles.grid}>
        {banks.map(bank => (
          <div
            key={bank.id}
            className={`${styles.bankCard} ${selectedBanks.includes(bank.id) ? styles.selected : ''}`}
            onClick={() => toggleBank(bank.id)}
            style={{
              '--bank-color': bank.color
            }}
          >
            <div className={styles.bankIcon} style={{ background: bank.color }}>
              {bank.name.charAt(0)}
            </div>
            <div className={styles.bankInfo}>
              <h3 className={styles.bankName}>{bank.name}</h3>
              <p className={styles.cardCount}>{bank.cards.length} kart</p>
            </div>
            {selectedBanks.includes(bank.id) && (
              <div className={styles.checkmark}>✓</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
