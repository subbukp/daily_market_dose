export interface Mmi {
  score: number;
  label: string;
}

export interface UsIndex {
  score: number;
  label: string;
  previousClose?: number;
}

export interface Metal {
  commodity: string;
  price: number;
  change: number;
  change_pct: number;
  change_usd: number;
  change_usd_pct: number;
  change_trade: number;
  change_trade_pct: number;
  currency: string;
  time: string;
}

export interface MetalsResponse {
  metals: Metal[];
}

export interface Bond {
  name: string;
  isin: string;
  bond_type: string;
  price: number;
  yield_pct: number;
  coupon_rate: number;
  maturity_date: string;
  credit_rating: string;
  rating_agency: string;
  rating_value: string;
  interest_freq: string;
  secured: boolean;
  yield_display: string;
  coupon_display: string;
}

export interface Ipo {
  company: string;
  category: string;
  open_date: string;
  close_date: string;
  listing_date: string;
  boa_date: string;
  price: string;
  issue_size_cr: string;
  lot_size: string;
  pe_ratio: string;
  gmp_value: string;
  gmp_percent: number;
  subscription: string;
  fire_rating: number;
  has_anchor: boolean;
  status: string;
  is_open: boolean;
  is_upcoming: boolean;
  status_emoji: string;
  gmp_display: string;
  fire_display: string;
  anchor_display: string;
}
