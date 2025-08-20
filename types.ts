import type { ReactNode } from 'react';



export interface SpaceDefenderProgress {
  weaponLevel: number;
  shieldLevel: number;
  speedLevel: number;
}

export interface StreetRacingProgress {
  currentCar: number;
  unlockedCars: number[];

  carUpgrades: {
      [key: number]: {
          speed: number;
          acceleration: number;
          handling: number;
          nitro: number;
      }
  };

  careerPoints: number;
  
  adProgress: {
    engine: number;
    tires: number;
    nitro: number;
  };
}


export interface User {
  id: number;
  name: string;
  coins: number;
  ton: number;
  referralEarnings: number;
  spins: number;
  adCredit: number;
  adsWatchedToday: number;
  tasksCompletedTodayForSpin: number;
  friendsInvitedTodayForSpin: number;
  spaceDefenderProgress: SpaceDefenderProgress;
  streetRacingProgress: StreetRacingProgress;
  banned?: boolean;
}


export interface AdminUser {
    id: number;
    username: string;
    password?: string; // Only for creation/update
    permissions: string[];
}


export interface UserCampaign {
  id: string;
  link: string;
  status: 'Active' | 'Paused' | 'Completed';
  completions: number;
  goal: number;
  cost: number;
  category?: 'Social' | 'Game';
}


export interface PartnerCampaign extends UserCampaign {
  requiredLevel: number;
}




export interface Friend {
  id: number;
  name: string;
}




export interface Task {
  id:string;
  icon: ReactNode;
  title: string;
  reward: number;
  claimed?: boolean;
  category?: 'Daily' | 'Game' | 'Social' | 'Partner';
}

export interface DailyTask extends Task {
    mandatory?: boolean;
    link?: string;
    action?: 'link' | 'share';
}
export interface GameTask extends Task {}



export interface Quest {
  id: string;
  icon: ReactNode;
  title: string;
  reward: number;
  currentProgress: number;
  totalProgress: number;
}

export interface Transaction {
  id: string;
  type: 'Withdrawal' | 'Deposit';
  amount: number;
  currency: 'TON' | 'Coins';
  date: string;
  status: 'Completed' | 'Pending' | 'Failed';
}

export interface CompletionTier {
  completions: number;
  cost: number;
}

export interface LanguageOption {
  id: string;
  name: string;
}




export interface PromoCode {
  code: string;
  type: 'COINS' | 'TON_AD_CREDIT' | 'SPINS';
  value: number;
  maxUses: number;
  usedBy: number[]; // array of user IDs
  expiresAt?: string; // ISO date string
}


export interface AdNetwork {
    id: string;
    name: string;
    code: string;
    enabled: boolean;
}

