'use client';

import { useState, useEffect } from 'react';
import styles from './CardSelector.module.css';

export default function CardSelector({ selectedBanks, onCardsChange }) {
  const [banks, setBanks] = useState([]);
  const [selectedCards, setSelectedCards] = useState([]);

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
    }
  };

  const toggleCard = (cardId) => {
    setSelectedCards(prev => {
      const newSelection = prev.includes(cardId)
        ? prev.filter(id => id !== cardId)
        : [...prev, cardId];

      onCardsChange(newSelection);
      return newSelection;
    });
  };

  const filteredBanks = banks.filter(bank => selectedBanks.includes(bank.id));

  if (selectedBanks.length === 0) {
    return (
      <div className={styles.empty}>
        <p className="text-muted">👆 Önce banka seçin</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <h2 className="heading-3">Kartlarınızı Seçin</h2>
      <p className="text-sm text-muted mb-lg">
        Birden fazla kart seçebilirsiniz
      </p>

      {filteredBanks.map(bank => (
        <div key={bank.id} className={styles.bankGroup}>
          <div className={styles.bankHeader}>
            <div
              className={styles.bankDot}
              style={{ background: bank.color }}
            />
            <h3 className={styles.bankName}>{bank.name}</h3>
          </div>

          <div className={styles.cardsGrid}>
            {bank.cards.map(card => (
              <div
                key={card.id}
                className={`${styles.cardChip} ${selectedCards.includes(card.id) ? styles.selected : ''}`}
                onClick={() => toggleCard(card.id)}
                style={{
                  '--bank-color': bank.color
                }}
              >
                <span className={styles.cardName}>{card.name}</span>
                {selectedCards.includes(card.id) && (
                  <span className={styles.chipClose}>✓</span>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}

      {selectedCards.length > 0 && (
        <div className={styles.summary}>
          <span className={styles.summaryText}>
            {selectedCards.length} kart seçildi
          </span>
        </div>
      )}
    </div>
  );
}
