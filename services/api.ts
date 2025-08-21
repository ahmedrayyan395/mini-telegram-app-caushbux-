import type { User, DailyTask, GameTask, Quest, Transaction, Friend, UserCampaign, PartnerCampaign, PromoCode, AdNetwork, AdminUser, Task } from '../types';
// We still need some constants for UI or initial state, but not the mock data arrays.
import { INITIAL_USER, ICONS } from '../constants';

// The base URL of your running Flask backend
const API_BASE_URL = 'http://127.0.0.1:5000';

// --- API Helper Functions ---

/**
 * In a real application, this ID would come from your authentication state
 * (e.g., stored in React Context or a state management library after login).
 * For now, it defaults to 1 to match the backend's default user.
 */
const getCurrentUserId = (): number => 1;








/**
 * Retrieves the stored admin authentication token from localStorage.
 */
const getAdminToken = (): string | null => {
    try {
        return localStorage.getItem('admin_token');
    } catch (e) {
        console.error("Could not access localStorage.", e);
        return null;
    }
};

/**
 * A centralized fetch wrapper to handle API requests, headers, and errors.
 * @param endpoint The API endpoint to call (e.g., '/user').
 * @param options The standard RequestInit options for fetch.
 */




/**
 * ========================================================================
 * DEVELOPMENT ONLY LOGIN METHOD
 */


export const devLogin = async (userId: number): Promise<User> => {
  // Use the apiFetch helper to make the network request.
  // It calls the backend endpoint we created: /dev/login/<user_id>
  const user = await apiFetch(`/dev/login/${userId}`, {
    method: 'POST',
    // No body is needed because the user's ID is in the URL.
  });

  
  return {
    ...user,
    spaceDefenderProgress: user.spaceDefenderProgress || INITIAL_USER.spaceDefenderProgress,
    streetRacingProgress: user.streetRacingProgress || INITIAL_USER.streetRacingProgress,
  };
};







// --- NEW Authentication Function ---








/**
 * Authenticates the user with the backend using the initData string from the Telegram Web App.
 * @param telegramInitData The raw initData string from window.Telegram.WebApp.initData
 * @returns The user object from the backend.
 */
export const loginWithTelegram = async (telegramInitData: string): Promise<User> => {
    const user = await apiFetch('/auth/telegram', {
        method: 'POST',
        // We don't need other headers here as this is the initial login.
        body: JSON.stringify({ initData: telegramInitData }),
    });
    // This function will now return the full user object, so we can use it directly.
    return {
      ...user,
      spaceDefenderProgress: user.spaceDefenderProgress || INITIAL_USER.spaceDefenderProgress,
      streetRacingProgress: user.streetRacingProgress || INITIAL_USER.streetRacingProgress,
    };
};




const apiFetch = async (endpoint: string, options: RequestInit = {}) => {
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
        // 'X-User-Id': String(getCurrentUserId()), // Identify the user for the backend
        ...options.headers,

        
    };

    const adminToken = getAdminToken();
    if (adminToken) {
        headers['Authorization'] = `Bearer ${adminToken}`;
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers,
            credentials: 'include',
        });

        if (!response.ok) {
            // Try to parse error details from the response body
            const errorData = await response.json().catch(() => ({ message: response.statusText }));
            throw { status: response.status, data: errorData };
        }
        
        // Handle responses that don't have a body (e.g., HTTP 204)
        if (response.status === 204) {
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error(`API Error on ${endpoint}:`, error);
        // Re-throw the error so UI components can handle it (e.g., show a notification)
        throw error;
    }
};


// --- User-facing API ---

export const fetchUser = async (): Promise<User> => {
  const user = await apiFetch('/user/me'); // Changed to a new endpoint like '/user/me'
  return {
      ...user,
      spaceDefenderProgress: user.spaceDefenderProgress || INITIAL_USER.spaceDefenderProgress,
      streetRacingProgress: user.streetRacingProgress || INITIAL_USER.streetRacingProgress,
  };
};

export const fetchDailyTasks = async (): Promise<DailyTask[]> => {
  return apiFetch('/daily-tasks');
};

export const fetchGameTasks = async (): Promise<GameTask[]> => {
  // The backend formats this response to match the mock's lightweight structure
  return apiFetch('/game-tasks');
};

export const fetchQuests = async (): Promise<Quest[]> => {
  return apiFetch('/quests'); // Backend returns an empty array
};

export const fetchTransactions = async (): Promise<Transaction[]> => {
  return apiFetch('/transactions');
};

export const fetchFriends = async (): Promise<Friend[]> => {
  return apiFetch('/friends'); // Backend returns an empty array
};

export const fetchUserCampaigns = async (): Promise<UserCampaign[]> => {
    return apiFetch('/user-campaigns');
};

export const fetchPartnerCampaigns = async (): Promise<PartnerCampaign[]> => {
    return apiFetch('/partner-campaigns');
};

export const addUserCampaign = async (campaignData: { link: string; goal: number; cost: number; }): Promise<{ success: boolean; message: string; newCampaign?: UserCampaign; user?: User; }> => {
    return apiFetch('/user-campaigns', {
        method: 'POST',
        body: JSON.stringify(campaignData),
    });
};

export const addPartnerTask = async (campaignData: { link: string; goal: number; cost: number; level: number }): Promise<{ success: boolean; message: string; newCampaign?: PartnerCampaign; user?: User; }> => {
    return apiFetch('/partner-tasks', {
        method: 'POST',
        body: JSON.stringify(campaignData),
    });
};

export const depositAdCredit = async (amount: number): Promise<{ success: boolean; user: User }> => {
    return apiFetch('/ad-credit/deposit', {
        method: 'POST',
        body: JSON.stringify({ amount }),
    });
};







export const claimDailyTask = async (taskId: string | number): Promise<{ success: boolean; user: User | null }> => {
  return apiFetch(`/daily-tasks/${taskId}/claim`, {
    method: 'POST',
  });
};

export const claimReferralEarnings = async (): Promise<{ success: boolean; user: User | null }> => {
    return apiFetch('/referrals/claim', {
        method: 'POST',
    });
}

export const executeWithdrawal = async (amountInTon: number): Promise<{ success: boolean; user: User | null }> => {
    return apiFetch('/withdrawals', {
        method: 'POST',
        body: JSON.stringify({ amountInTon }),
    });
}

export const spinWheel = async (): Promise<{ success: boolean; prize: { type: string; value: number; label: string; }; user: User }> => {
    return apiFetch('/spin-wheel', {
        method: 'POST',
    });
};

export const watchAdForSpin = async(): Promise<{success: boolean; message: string; user?: User}> => {
    return apiFetch('/spins/watch-ad', {
        method: 'POST',
    });
}

export const completeTaskForSpin = async(): Promise<{success: boolean; message: string; user?: User}> => {
    return apiFetch('/spins/complete-task', {
        method: 'POST',
    });
}

export const inviteFriendForSpin = async(): Promise<{success: boolean; message: string; user?: User}> => {
    return apiFetch('/spins/invite-friend', {
        method: 'POST',
    });
}

export const buySpins = async (packageId: string, currency: 'TON' | 'COINS'): Promise<{ success: boolean; message: string; user?: User; }> => {
    return apiFetch('/spins/buy', {
        method: 'POST',
        body: JSON.stringify({ packageId, currency }),
    });
};

export const redeemPromoCode = async (code: string): Promise<{ success: boolean; message: string; user?: User; }> => {
    return apiFetch('/promo-codes/redeem', {
        method: 'POST',
        body: JSON.stringify({ code }),
    });
};

// --- Admin-facing API ---

export const adminLogin = async (username: string, password: string): Promise<{ success: boolean, token?: string }> => {
    const response = await apiFetch('/admin/login', {
        method: 'POST',
        // We don't need the user/admin headers for the login itself
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });

    if (response.success && response.token) {
        try {
            localStorage.setItem('admin_token', response.token);
        } catch (e) {
            console.error("Failed to save admin token to localStorage.", e);
        }
    }
    return response;
};

export const adminLogout = (): void => {
    try {
        localStorage.removeItem('admin_token');
    } catch (e) {
        console.error("Failed to remove admin token from localStorage.", e);
    }
};

export const fetchDashboardStats = async () => {
    return apiFetch('/admin/dashboard-stats');
};

export const fetchAllUsers = async (): Promise<User[]> => {
    return apiFetch('/admin/users');
};

export const updateUser = async (userId: number, data: Partial<User>): Promise<{ success: boolean, user?: User }> => {
    return apiFetch(`/admin/users/${userId}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
    });
};

export const fetchAllPromoCodes = async (): Promise<PromoCode[]> => {
    return apiFetch('/admin/promo-codes');
};

export const createPromoCode = async (data: Omit<PromoCode, 'usedBy'>): Promise<{ success: boolean, code?: PromoCode }> => {
    return apiFetch('/admin/promo-codes', {
        method: 'POST',
        body: JSON.stringify(data),
    });
};

export const fetchSettings = async () => {
    return apiFetch('/admin/settings');
};

export const updateSettings = async (newSettings: Partial<any>): Promise<{ success: boolean, settings?: any }> => {
    return apiFetch('/admin/settings', {
        method: 'PATCH',
        body: JSON.stringify(newSettings),
    });
};

export const createAdminTask = async (task: Omit<Task, 'id' | 'icon'>): Promise<{ success: boolean, task?: Task }> => {
    return apiFetch('/admin/tasks', {
        method: 'POST',
        body: JSON.stringify(task),
    });
};