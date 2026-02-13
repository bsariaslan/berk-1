'use client';

import styles from './CampaignCard.module.css';

export default function CampaignCard({ campaign }) {
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('tr-TR', {
      style: 'currency',
      currency: 'TRY',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDiscount = () => {
    if (campaign.discount_type === 'percentage') {
      return `%${(campaign.discount_rate * 100).toFixed(0)} indirim`;
    } else {
      return `${formatCurrency(campaign.discount_rate)} indirim`;
    }
  };

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <h4 className={styles.title}>{campaign.title}</h4>
        <div className={styles.savingsBadge}>
          {formatCurrency(campaign.savings)} kazanç
        </div>
      </div>

      {campaign.description && (
        <p className={styles.description}>{campaign.description}</p>
      )}

      <div className={styles.details}>
        <div className={styles.detailItem}>
          <span className={styles.detailIcon}>💰</span>
          <span className={styles.detailText}>{formatDiscount()}</span>
        </div>

        {campaign.max_discount && (
          <div className={styles.detailItem}>
            <span className={styles.detailIcon}>🎯</span>
            <span className={styles.detailText}>
              Max {formatCurrency(campaign.max_discount)}
            </span>
          </div>
        )}

        {campaign.min_spend > 0 && (
          <div className={styles.detailItem}>
            <span className={styles.detailIcon}>📊</span>
            <span className={styles.detailText}>
              Min {formatCurrency(campaign.min_spend)}
            </span>
          </div>
        )}
      </div>

      {campaign.conditions && (
        <div className={styles.conditions}>
          <span className={styles.conditionsIcon}>ℹ️</span>
          <span className={styles.conditionsText}>{campaign.conditions}</span>
        </div>
      )}

      {campaign.source_url && (
        <a
          href={campaign.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className={styles.link}
        >
          Detaylar →
        </a>
      )}
    </div>
  );
}
