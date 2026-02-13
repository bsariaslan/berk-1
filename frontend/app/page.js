'use client';

import { useState } from 'react';
import BankSelector from '@/components/BankSelector';
import CardSelector from '@/components/CardSelector';
import SpendingForm from '@/components/SpendingForm';
import ResultsPanel from '@/components/ResultsPanel';
import styles from './page.module.css';

export default function Home() {
  const [selectedBanks, setSelectedBanks] = useState([]);
  const [selectedCards, setSelectedCards] = useState([]);
  const [results, setResults] = useState(null);

  const handleBanksChange = (banks) => {
    setSelectedBanks(banks);
    // Seçili bankalara ait olmayan kartları temizle
    if (banks.length === 0) {
      setSelectedCards([]);
    }
  };

  const handleCardsChange = (cards) => {
    setSelectedCards(cards);
  };

  const handleCompare = (compareResults) => {
    setResults(compareResults);
    // Sonuçlara scroll
    setTimeout(() => {
      document.getElementById('results')?.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }, 100);
  };

  const handleReset = () => {
    setResults(null);
    setSelectedCards([]);
    setSelectedBanks([]);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <main className="container">
      {/* Header */}
      <header className={styles.header}>
        <h1 className="heading-1">💳 Hangi Kartla Alışveriş Yapmalıyım?</h1>
        <p className="text-lg text-muted">
          Kartlarınızı seçin, harcama bilgilerinizi girin ve en avantajlı kampanyayı bulun!
        </p>
      </header>

      {/* Step 1: Bank & Card Selection */}
      <section className={`glass-card ${styles.section}`}>
        <div className={styles.stepBadge}>Adım 1</div>
        <BankSelector onBanksChange={handleBanksChange} />
        <CardSelector selectedBanks={selectedBanks} onCardsChange={handleCardsChange} />
      </section>

      {/* Step 2: Spending Information */}
      {selectedCards.length > 0 && (
        <section className={`glass-card ${styles.section} fade-in`}>
          <div className={styles.stepBadge}>Adım 2</div>
          <SpendingForm selectedCards={selectedCards} onCompare={handleCompare} />
        </section>
      )}

      {/* Step 3: Results */}
      {results && (
        <section id="results" className={styles.section}>
          <div className={styles.resultsHeader}>
            <h2 className="heading-2">📊 Sonuçlar</h2>
            <button onClick={handleReset} className="btn btn-secondary">
              🔄 Yeni Karşılaştırma
            </button>
          </div>
          <ResultsPanel
            results={results}
            merchant={results.merchant}
            amount={results.amount}
          />
        </section>
      )}

      {/* Footer */}
      <footer className={styles.footer}>
        <p className="text-sm text-muted">
          Kampanya bilgileri banka kaynaklarından alınmaktadır. Güncel kampanya koşulları için banka web sitelerini ziyaret edin.
        </p>
      </footer>
    </main>
  );
}
