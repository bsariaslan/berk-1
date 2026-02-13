'use client';

import CampaignCard from './CampaignCard';
import styles from './ResultsPanel.module.css';

export default function ResultsPanel({ results, merchant, amount }) {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('tr-TR', {
      style: 'currency',
      currency: 'TRY',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  if (!results) {
    return null;
  }

  if (results.results.length === 0) {
    return (
      <div className={`glass-card fade-in ${styles.empty}`}>
        <div className={styles.emptyIcon}>😔</div>
        <h3 className="heading-3">Kampanya Bulunamadı</h3>
        <p className="text-md text-muted">
          <strong>{merchant}</strong> için seçtiğiniz kartlarda aktif kampanya bulunamadı.
        </p>
        <p className="text-sm text-muted" style={{ marginTop: '0.5rem' }}>
          Farklı bir mağaza deneyin veya başka kartlarınızı ekleyin.
        </p>
      </div>
    );
  }

  const bestCard = results.results[0];

  return (
    <div className="fade-in">
      {/* En İyi Öneri */}
      <div className={`glass-card ${styles.bestCard}`}>
        <div className={styles.bestBadge}>🏆 En Avantajlı</div>
        <div className={styles.bestHeader}>
          <div>
            <h3 className={styles.bestCardName}>{bestCard.card_name}</h3>
            <p className={styles.bestBankName}>
              <span
                className={styles.bankDot}
                style={{ background: bestCard.bank_color }}
              />
              {bestCard.bank_name}
            </p>
          </div>
          <div className={styles.bestSavings}>
            <div className={styles.savingsAmount}>
              {formatCurrency(bestCard.total_savings)}
            </div>
            <div className={styles.savingsLabel}>toplam kazanç</div>
          </div>
        </div>

        <div className={styles.campaigns}>
          {bestCard.campaigns.map(campaign => (
            <CampaignCard key={campaign.campaign_id} campaign={campaign} />
          ))}
        </div>
      </div>

      {/* Diğer Kartlar */}
      {results.results.length > 1 && (
        <div style={{ marginTop: '2rem' }}>
          <h3 className="heading-3" style={{ marginBottom: '1rem' }}>
            Diğer Seçenekler
          </h3>

          {results.results.slice(1).map((card, index) => (
            <div
              key={card.card_id}
              className={`glass-card ${styles.otherCard}`}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className={styles.cardHeader}>
                <div>
                  <h4 className={styles.cardName}>{card.card_name}</h4>
                  <p className={styles.bankName}>
                    <span
                      className={styles.bankDot}
                      style={{ background: card.bank_color }}
                    />
                    {card.bank_name}
                  </p>
                </div>
                <div className={styles.savings}>
                  {formatCurrency(card.total_savings)}
                </div>
              </div>

              <div className={styles.campaigns}>
                {card.campaigns.map(campaign => (
                  <CampaignCard key={campaign.campaign_id} campaign={campaign} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Özet Bilgi */}
      <div className={styles.summary}>
        <p className="text-sm text-muted">
          <strong>{merchant}</strong> için {formatCurrency(amount)} harcamanızda,{' '}
          {results.results.length} karttan {results.results.length === 1 ? 'kampanya' : 'kampanyalar'} bulundu.
        </p>
      </div>
    </div>
  );
}
