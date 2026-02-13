'use client';

import { useState, useEffect } from 'react';
import styles from './SpendingForm.module.css';

export default function SpendingForm({ selectedCards, onCompare }) {
  const [merchant, setMerchant] = useState('');
  const [amount, setAmount] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSuggestions();
  }, []);

  const fetchSuggestions = async () => {
    try {
      const response = await fetch('/api/compare');
      const data = await response.json();
      if (data.success) {
        setSuggestions(data.data);
      }
    } catch (error) {
      console.error('Öneriler yüklenemedi:', error);
    }
  };

  const handleMerchantChange = (e) => {
    const value = e.target.value;
    setMerchant(value);
    setShowSuggestions(value.length > 0);
  };

  const selectSuggestion = (suggestion) => {
    setMerchant(suggestion);
    setShowSuggestions(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!merchant.trim()) {
      alert('Lütfen mağaza/site adı girin');
      return;
    }

    if (!amount || amount <= 0) {
      alert('Lütfen geçerli bir tutar girin');
      return;
    }

    if (selectedCards.length === 0) {
      alert('Lütfen en az bir kart seçin');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          selectedCards,
          merchant: merchant.trim(),
          amount: parseFloat(amount)
        })
      });

      const data = await response.json();

      if (data.success) {
        onCompare(data.data);
      } else {
        alert(data.error || 'Bir hata oluştu');
      }
    } catch (error) {
      console.error('Karşılaştırma hatası:', error);
      alert('Karşılaştırma yapılırken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const filteredSuggestions = suggestions.filter(s =>
    s.toLowerCase().includes(merchant.toLowerCase())
  ).slice(0, 5);

  const isDisabled = selectedCards.length === 0 || loading;

  return (
    <div className={styles.container}>
      <h2 className="heading-3">Harcama Bilgileri</h2>

      <form onSubmit={handleSubmit} className={styles.form}>
        <div className="input-group">
          <label className="input-label">Nerede harcama yapacaksınız?</label>
          <div className={styles.autocompleteWrapper}>
            <input
              type="text"
              className="input"
              placeholder="Örn: Trendyol, Hepsiburada, Migros..."
              value={merchant}
              onChange={handleMerchantChange}
              onFocus={() => setShowSuggestions(merchant.length > 0)}
              disabled={isDisabled}
            />
            {showSuggestions && filteredSuggestions.length > 0 && (
              <div className={styles.suggestions}>
                {filteredSuggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    className={styles.suggestionItem}
                    onClick={() => selectSuggestion(suggestion)}
                  >
                    <span className={styles.suggestionIcon}>🏪</span>
                    {suggestion}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="input-group">
          <label className="input-label">Ne kadar harcayacaksınız?</label>
          <div className={styles.amountWrapper}>
            <input
              type="number"
              className={`input ${styles.amountInput}`}
              placeholder="0"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              min="0"
              step="0.01"
              disabled={isDisabled}
            />
            <span className={styles.currency}>₺</span>
          </div>
        </div>

        <button
          type="submit"
          className="btn btn-primary btn-lg"
          disabled={isDisabled}
          style={{ width: '100%', marginTop: '1rem' }}
        >
          {loading ? (
            <>
              <div className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></div>
              Karşılaştırılıyor...
            </>
          ) : (
            '🎯 Karşılaştır'
          )}
        </button>
      </form>
    </div>
  );
}
