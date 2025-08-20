import type { User, DailyTask, GameTask, Quest, Transaction, Friend, UserCampaign, PartnerCampaign, PromoCode, AdNetwork, AdminUser, Task } from '../types';
import { INITIAL_USER, DAILY_TASKS, GAME_TASKS, QUESTS, TRANSACTIONS, CONVERSION_RATE, MOCK_FRIENDS, MOCK_USER_CAMPAIGNS, MOCK_PROMO_CODES, SPIN_WHEEL_PRIZES, SPIN_STORE_PACKAGES, MOCK_ADMINS, generateMockUsers, ICONS } from '../constants';


// In-memory store
let users: User[] = [ { ...INITIAL_USER }, ...generateMockUsers(50) ];
let dailyTasks: DailyTask[] = [...DAILY_TASKS];
let gameTasks: UserCampaign[] = [...MOCK_USER_CAMPAIGNS].filter(c => c.category === 'Game');
let socialTasks: UserCampaign[] = [...MOCK_USER_CAMPAIGNS].filter(c => c.category === 'Social');
let partnerCampaigns: PartnerCampaign[] = [];
let quests: Quest[] = [...QUESTS];
let transactions: Transaction[] = [...TRANSACTIONS];
let userCampaigns: UserCampaign[] = [...MOCK_USER_CAMPAIGNS];
let promoCodes: PromoCode[] = [...MOCK_PROMO_CODES];
let admins: AdminUser[] = [...MOCK_ADMINS];
let settings = {
    autoWithdrawals: false,
    adNetworks: [
        { id: 'libtl', name: 'libtl.com', code: `<script src='//libtl.com/sdk.js' data-zone='9692552' data-sdk='show_9692552'></script>`, enabled: true },
    ] as AdNetwork[]
};


const simulateDelay = (delay = 500) => new Promise(resolve => setTimeout(resolve, delay));


// --- User-facing API ---

export const fetchUser = async (): Promise<User> => {
  await simulateDelay();
  
  const user = users[0];
  if (!user.spaceDefenderProgress) {
    user.spaceDefenderProgress = { ...INITIAL_USER.spaceDefenderProgress };
  }
  if (!user.streetRacingProgress) {
    user.streetRacingProgress = { ...INITIAL_USER.streetRacingProgress };
  }
  return { ...user };
};

export const fetchDailyTasks = async (): Promise<DailyTask[]> => {
  await simulateDelay();
  return [...dailyTasks];
};

export const fetchGameTasks = async (): Promise<GameTask[]> => {
  await simulateDelay();
  // This is now mapped from the userCampaigns store for consistency
  return gameTasks.map(c => ({
      id: c.id,
      icon: ICONS.game,
      title: 'Play ' + (new URL(c.link).hostname),
      reward: (c.cost / (c.goal || 1)) * 0.4 * CONVERSION_RATE,
  }));
};

export const fetchQuests = async (): Promise<Quest[]> => {
  await simulateDelay();
  return [...quests];
};

export const fetchTransactions = async (): Promise<Transaction[]> => {
  await simulateDelay(800);
  return [...transactions];
};

export const fetchFriends = async (): Promise<Friend[]> => {
  await simulateDelay(300);
  return [...MOCK_FRIENDS];
};

export const fetchUserCampaigns = async (): Promise<UserCampaign[]> => {
    await simulateDelay(600); // jsut an api call to fetch all the user camaigns
    return [...userCampaigns];
};

export const fetchPartnerCampaigns = async (): Promise<PartnerCampaign[]> => {
    await simulateDelay(700);
    return [...partnerCampaigns];
};

export const addUserCampaign = async (campaignData: { link: string; goal: number; cost: number; }): Promise<{ success: boolean; message: string; newCampaign?: UserCampaign; user?: User; }> => {
    await simulateDelay(1000);
    if (users[0].adCredit < campaignData.cost) {
        return { success: false, message: "Insufficient ad balance. Please add funds." };
    }
    users[0].adCredit -= campaignData.cost;
    const newCampaign: UserCampaign = {
        id: `uc${Date.now()}`,
        link: campaignData.link,
        status: 'Active',
        completions: 0,
        goal: campaignData.goal,
        cost: campaignData.cost,
        category: 'Social'
    };
    userCampaigns.unshift(newCampaign);
    socialTasks.unshift(newCampaign);
    return { success: true, message: 'Campaign created successfully!', newCampaign, user: { ...users[0] } };
};

export const addPartnerTask = async (campaignData: { link: string; goal: number; cost: number; level: number }): Promise<{ success: boolean; message: string; newCampaign?: PartnerCampaign; user?: User; }> => {
    await simulateDelay(1000);
    if (users[0].adCredit < campaignData.cost) {
        return { success: false, message: "Insufficient ad balance. Please add funds." };
    }
    users[0].adCredit -= campaignData.cost;
    const newCampaign: PartnerCampaign = {
        id: `pc${Date.now()}`,
        link: campaignData.link,
        status: 'Active',
        completions: 0,
        goal: campaignData.goal,
        cost: campaignData.cost,
        requiredLevel: campaignData.level
    };
    partnerCampaigns.unshift(newCampaign);
    return { success: true, message: 'Partner task created successfully!', newCampaign, user: { ...users[0] } };
};

export const depositAdCredit = async (amount: number): Promise<{ success: boolean; user: User }> => {
    await simulateDelay(1000);
    users[0].adCredit += amount;
    transactions.unshift({
        id: `d${Date.now()}`,
        type: 'Deposit',
        amount: amount,
        currency: 'TON',
        date: new Date().toISOString().split('T')[0],
        status: 'Completed'
    });
    return { success: true, user: { ...users[0] } };
};

export const claimDailyTask = async (taskId: string): Promise<{ success: boolean; user: User | null }> => {
  await simulateDelay();
  const taskIndex = dailyTasks.findIndex(t => t.id === taskId);
  if (taskIndex !== -1 && !dailyTasks[taskIndex].claimed) {
    users[0].coins += dailyTasks[taskIndex].reward;
    dailyTasks[taskIndex].claimed = true;
    
    // Grant a spin for completing a task
    if (users[0].tasksCompletedTodayForSpin < 50) {
      users[0].spins += 1;
      users[0].tasksCompletedTodayForSpin += 1;
    }

    return { success: true, user: { ...users[0] } };
  }
  return { success: false, user: null };
};

export const claimReferralEarnings = async (): Promise<{ success: boolean; user: User | null }> => {
    await simulateDelay();
    if(users[0].referralEarnings > 0) {
        users[0].coins += users[0].referralEarnings;
        users[0].referralEarnings = 0;
        return { success: true, user: { ...users[0] } };
    }
    return { success: false, user: null };
}

export const executeWithdrawal = async (amountInTon: number): Promise<{ success: boolean; user: User | null }> => {
    await simulateDelay(1500);
    const amountInCoins = amountInTon * CONVERSION_RATE;
    if (users[0].coins >= amountInCoins) {
        users[0].coins -= amountInCoins;
        users[0].ton += amountInTon;
        
        transactions.unshift({
            id: `t${Date.now()}`,
            type: 'Withdrawal',
            amount: amountInTon,
            currency: 'TON',
            date: new Date().toISOString().split('T')[0],
            status: 'Completed'
        });
        return { success: true, user: { ...users[0] } };
    }
    return { success: false, user: null };
}

export const spinWheel = async (): Promise<{ success: boolean; prize: { type: string; value: number; label: string; }; user: User }> => {
    await simulateDelay(100);

    if (users[0].spins <= 0) {
      return {
        success: false,
        prize: { type: 'ERROR', value: 0, label: 'No spins left' },
        user: { ...users[0] }
      };
    }

    users[0].spins -= 1;

    const totalWeight = SPIN_WHEEL_PRIZES.reduce((acc, prize) => acc + prize.weight, 0);
    let randomWeight = Math.random() * totalWeight;
    let selectedPrize = SPIN_WHEEL_PRIZES[SPIN_WHEEL_PRIZES.length - 1]; // fallback

    for (const prize of SPIN_WHEEL_PRIZES) {
        if (randomWeight < prize.weight) {
            selectedPrize = prize;
            break;
        }
        randomWeight -= prize.weight;
    }
    
    if (selectedPrize.type === 'COINS') {
        users[0].coins += selectedPrize.value;
    }

    return {
        success: true,
        prize: selectedPrize,
        user: { ...users[0] }
    };
};

export const watchAdForSpin = async(): Promise<{success: boolean; message: string; user?: User}> => {
    await simulateDelay(200);
    if (users[0].adsWatchedToday >= 50) {
        return { success: false, message: "Daily limit for ad spins reached." };
    }
    users[0].adsWatchedToday += 1;
    users[0].spins += 1;
    return { success: true, message: "+1 Spin!", user: { ...users[0] } };
}

export const completeTaskForSpin = async(): Promise<{success: boolean; message: string; user?: User}> => {
    await simulateDelay(50);
     if (users[0].tasksCompletedTodayForSpin >= 50) {
        return { success: false, message: "Daily limit for task spins reached." };
    }
    users[0].tasksCompletedTodayForSpin += 1;
    users[0].spins += 1;
    return { success: true, message: "+1 Spin for completing a task!", user: { ...users[0] } };
}

export const inviteFriendForSpin = async(): Promise<{success: boolean; message: string; user?: User}> => {
    await simulateDelay(50);
     if (users[0].friendsInvitedTodayForSpin >= 50) {
        return { success: false, message: "Daily limit for friend invite spins reached." };
    }
    users[0].friendsInvitedTodayForSpin += 1;
    users[0].spins += 1;
    return { success: true, message: "+1 Spin for inviting a friend!", user: { ...users[0] } };
}

export const buySpins = async (packageId: string, currency: 'TON' | 'COINS'): Promise<{ success: boolean; message: string; user?: User; }> => {
    await simulateDelay(1000);
    const selectedPackage = SPIN_STORE_PACKAGES.find(p => p.id === packageId);
    if (!selectedPackage) {
        return { success: false, message: "Invalid package selected." };
    }
    
    if (currency === 'TON') {
        // Handled client-side, just award spins
    } else { // currency === 'COINS'
        const costInCoins = selectedPackage.costTon * CONVERSION_RATE;
        if (users[0].coins < costInCoins) {
            return { success: false, message: "Insufficient coin balance." };
        }
        users[0].coins -= costInCoins;
    }

    users[0].spins += selectedPackage.spins;

    return {
        success: true,
        message: `Successfully purchased ${selectedPackage.spins.toLocaleString()} spins!`,
        user: { ...users[0] }
    };
};

export const redeemPromoCode = async (code: string): Promise<{ success: boolean; message: string; user?: User; }> => {
    await simulateDelay(400);
    const promoCode = promoCodes.find(p => p.code.toLowerCase() === code.toLowerCase());

    if (!promoCode) {
        return { success: false, message: 'Invalid promo code.' };
    }
    if (promoCode.usedBy.length >= promoCode.maxUses) {
        return { success: false, message: 'This promo code has reached its usage limit.' };
    }
    if (promoCode.expiresAt && new Date(promoCode.expiresAt) < new Date()) {
        return { success: false, message: 'This promo code has expired.' };
    }
    if (promoCode.usedBy.includes(users[0].id)) {
        return { success: false, message: 'You have already used this promo code.' };
    }

    let rewardMessage = '';
    switch (promoCode.type) {
        case 'COINS':
            users[0].coins += promoCode.value;
            rewardMessage = `${promoCode.value.toLocaleString()} Coins`;
            break;
        case 'SPINS':
            users[0].spins += promoCode.value;
            rewardMessage = `${promoCode.value} free spin(s)`;
            break;
        case 'TON_AD_CREDIT':
            users[0].adCredit += promoCode.value;
            rewardMessage = `${promoCode.value} TON in ad credits`;
            break;
    }

    promoCode.usedBy.push(users[0].id);
    
    return {
        success: true,
        message: `Successfully redeemed! You received ${rewardMessage}.`,
        user: { ...users[0] }
    };
};

// --- Admin-facing API ---

export const adminLogin = async (username: string, password: string): Promise<{ success: boolean, token?: string }> => {
    await simulateDelay();
    const admin = admins.find(a => a.username === username && a.password === password);
    if (admin) {
        return { success: true, token: `mock_token_${admin.id}` };
    }
    return { success: false };
};

export const fetchDashboardStats = async () => {
    await simulateDelay();
    const totalUsers = users.length;
    const totalCoins = users.reduce((acc, u) => acc + u.coins, 0);
    const totalWithdrawals = transactions.filter(t => t.type === 'Withdrawal').reduce((acc, t) => acc + t.amount, 0);
    const tasksCompleted = dailyTasks.filter(t => t.claimed).length;
    return { totalUsers, totalCoins, totalWithdrawals, tasksCompleted };
};

export const fetchAllUsers = async (): Promise<User[]> => {
    await simulateDelay();
    return [...users];
};

export const updateUser = async (userId: number, data: Partial<User>): Promise<{ success: boolean, user?: User }> => {
    await simulateDelay();
    const userIndex = users.findIndex(u => u.id === userId);
    if (userIndex !== -1) {
        users[userIndex] = { ...users[userIndex], ...data };
        return { success: true, user: users[userIndex] };
    }
    return { success: false };
};

export const fetchAllPromoCodes = async (): Promise<PromoCode[]> => {
    await simulateDelay();
    return [...promoCodes];
};

export const createPromoCode = async (data: Omit<PromoCode, 'usedBy'>): Promise<{ success: boolean, code?: PromoCode }> => {
    await simulateDelay();
    if (promoCodes.some(p => p.code.toLowerCase() === data.code.toLowerCase())) {
        return { success: false };
    }
    const newCode = { ...data, usedBy: [] };
    promoCodes.unshift(newCode);
    return { success: true, code: newCode };
};

export const fetchSettings = async () => {
    await simulateDelay();
    return { ...settings, admins: [...admins] };
};

export const updateSettings = async (newSettings: Partial<typeof settings>): Promise<{ success: boolean, settings?: typeof settings }> => {
    await simulateDelay();
    settings = { ...settings, ...newSettings };
    return { success: true, settings: { ...settings }};
};

export const createAdminTask = async (task: Omit<Task, 'id' | 'icon'>): Promise<{ success: boolean, task?: Task }> => {
    await simulateDelay();
    const newTask: Task = {
        ...task,
        id: `task-${Date.now()}`,
        icon: ICONS.tasks, // Generic icon for admin-added tasks
    };

    switch (task.category) {
        case 'Daily':
            dailyTasks.push({ ...newTask, mandatory: false });
            break;
        case 'Game':
             gameTasks.push({
                id: newTask.id,
                link: 'https://t.me/example_game_bot',
                status: 'Active',
                completions: 0,
                goal: 1, // Simplified
                cost: 0.1, // Simplified
                category: 'Game'
            });
            break;
        case 'Social':
            socialTasks.push({
                id: newTask.id,
                link: 'https://t.me/example_social_channel',
                status: 'Active',
                completions: 0,
                goal: 1, // Simplified
                cost: 0.1, // Simplified
                category: 'Social'
            });
            break;
        case 'Partner':
             partnerCampaigns.push({
                id: newTask.id,
                link: 'https://t.me/example_partner_bot',
                status: 'Active',
                completions: 0,
                goal: 1,
                cost: 1,
                requiredLevel: 5,
                category: 'Game' // Partner tasks are a form of game task
             });
             break;
        default:
            return { success: false };
    }
    return { success: true, task: newTask };
};
