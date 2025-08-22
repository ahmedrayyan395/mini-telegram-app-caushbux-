import React, { useState, useEffect } from 'react';
import type { DailyTask, GameTask, User, PartnerCampaign, UserCampaign } from '../types';
import { fetchDailyTasks, claimDailyTask, fetchPartnerCampaigns, fetchUserCampaigns, redeemPromoCode, completeTaskForSpin } from '../services/api';
import { ICONS, CONVERSION_RATE } from '../constants';

// Declare the ad SDK function to make it available in the component
declare const show_9692552: (type?: 'pop') => Promise<void>;

const DailyTaskItem: React.FC<{ task: DailyTask; onClaim: (id: string) => void }> = ({ task, onClaim }) => {

  const isClaimable = !task.claimed;

  const getButtonContent = () => {
    
    if (task.claimed) return 'Claimed';
    if (task.action === 'share') return 'Share';
    if (task.action === 'link') return 'Subscribe';
    return 'Claim';
  };

  return (
    <div className="bg-slate-800 p-4 rounded-lg flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <div className="bg-slate-700 p-3 rounded-full text-green-500">{task.icon}</div>
        <div>
          <h3 className="font-semibold text-white">{task.title}</h3>
          <p className="text-sm text-slate-400">+{task.reward.toLocaleString()} Coins</p>
        </div>
      </div>
      <button
        onClick={() => isClaimable && onClaim(task.id)}
        disabled={!isClaimable}
        className={`font-bold py-2 px-4 rounded-lg text-sm transition-colors w-24 text-center ${
          task.claimed
            ? 'bg-slate-600 text-slate-400 cursor-not-allowed'
            : 'bg-green-500 text-white hover:bg-green-600'
        }`}
      >
        {getButtonContent()}
      </button>
    </div>
  );
};

const CampaignTaskItem: React.FC<{ task: UserCampaign; icon: React.ReactNode; description: string; buttonClass: string; onStart: () => void }> = ({ task, icon, description, buttonClass, onStart }) => {
  const reward = (task.cost / (task.goal || 1)) * 0.4 * CONVERSION_RATE;
  let taskName = 'Campaign Task';
  try {
    const rawName = new URL(task.link).pathname.split('/')[1];
    taskName = rawName?.replace(/^my_?/i, '').replace(/_/g, ' ') || taskName;
  } catch (e) {
      console.error("Invalid campaign link URL:", task.link);
  }
  const title = taskName.charAt(0).toUpperCase() + taskName.slice(1);


  return (
    <div className="bg-slate-800 p-4 rounded-lg flex items-center justify-between">
      <div className="flex items-center space-x-4 flex-grow min-w-0">
        <div className={`bg-slate-700 p-3 rounded-full flex-shrink-0 ${buttonClass.split(' ')[0]}`}>{icon}</div>
        <div className="flex-grow min-w-0">
          <h3 className="font-semibold text-white truncate" title={title}>{title}</h3>
          <p className="text-sm text-slate-400">{description}</p>
          <p className="text-sm text-green-400 mt-1">+{reward.toLocaleString()} Coins</p>
        </div>
      </div>
      <a
        href={task.link}
        target="_blank"
        rel="noopener noreferrer"
        onClick={onStart}
        className={`${buttonClass} text-white font-bold py-2 px-4 rounded-lg text-sm transition-colors flex-shrink-0 ml-2`}
      >
        Start
      </a>
    </div>
  );
};


const PartnerTaskItem: React.FC<{ task: PartnerCampaign, onStart: () => void }> = ({ task, onStart }) => {
  const reward = (task.cost / (task.goal || 1)) * 0.4 * CONVERSION_RATE;
  let botName = 'Partner Bot';
  try {
    const rawName = new URL(task.link).pathname.split('/')[1];
    botName = rawName?.replace(/^my_?/i, '').replace(/_/g, ' ') || botName;
  } catch (e)      {
      console.error("Invalid partner link URL:", task.link);
  }
  const title = botName.charAt(0).toUpperCase() + botName.slice(1);

  return (
    <div className="bg-slate-800 p-4 rounded-lg flex items-center justify-between">
      <div className="flex items-center space-x-4 flex-grow min-w-0">
        <div className="bg-slate-700 p-3 rounded-full text-blue-500 flex-shrink-0">{ICONS.gift}</div>
        <div className="flex-grow min-w-0">
          <h3 className="font-semibold text-white truncate">{title}</h3>
          <p className="text-sm text-slate-400">Reach level {task.requiredLevel}</p>
          <p className="text-sm text-green-400 mt-1">+{reward.toLocaleString()} Coins</p>
        </div>
      </div>
      <a
        href={task.link}
        target="_blank"
        rel="noopener noreferrer"
        onClick={onStart}
        className="bg-blue-500 text-white font-bold py-2 px-4 rounded-lg text-sm hover:bg-blue-600 transition-colors flex-shrink-0 ml-2"
      >
        Start
      </a>
    </div>
  );
};

const TasksLockedOverlay = () => (
    <div className="absolute inset-0 bg-slate-900/80 backdrop-blur-sm z-10 flex flex-col items-center justify-center text-center p-4 rounded-lg">
        <div className="w-16 h-16 mb-4 text-slate-500">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
        </div>
        <h3 className="text-xl font-bold text-white">Tasks Locked</h3>
        <p className="text-slate-400 mt-2">Please complete all mandatory daily tasks to unlock more ways to earn.</p>
    </div>
);

const PromoCodeSection: React.FC<{ setUser: (user: User) => void }> = ({ setUser }) => {
  const [code, setCode] = useState('');
  const [feedback, setFeedback] = useState<{ message: string; isError: boolean } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleRedeem = async () => {
    if (!code || isLoading) return;
    setIsLoading(true);
    setFeedback(null);

    const result = await redeemPromoCode(code);
    
    setFeedback({ message: result.message, isError: !result.success });
    if (result.success && result.user) {
      setUser(result.user);
      setCode(''); // Clear input on success
    }
    setIsLoading(false);
  };

  return (
    <section>
        <h2 className="text-xl font-bold mb-4 text-white">Promo Code</h2>
        <div className="bg-slate-800 p-4 rounded-lg space-y-3">
            <div className="flex space-x-2">
                <input
                    type="text"
                    value={code}
                    onChange={(e) => setCode(e.target.value.toUpperCase())}
                    placeholder="ENTER PROMO CODE"
                    className="flex-grow bg-slate-700 border border-slate-600 rounded-lg p-3 text-white placeholder-slate-400 focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none transition uppercase"
                    disabled={isLoading}
                    aria-label="Promo Code Input"
                />
                <button
                    onClick={handleRedeem}
                    disabled={!code || isLoading}
                    className="bg-green-500 text-white font-bold py-3 px-6 rounded-lg transition-colors hover:bg-green-600 disabled:bg-slate-600 disabled:cursor-not-allowed"
                    aria-label="Apply Promo Code"
                >
                    {isLoading ? '...' : 'Apply'}
                </button>
            </div>
            {feedback && (
                <p className={`text-sm text-center font-semibold pt-2 ${feedback.isError ? 'text-red-500' : 'text-green-500'}`}>
                    {feedback.message}
                </p>
            )}
        </div>
    </section>
  );
};


const EarningsPage: React.FC<{ setUser: (user: User) => void }> = ({ setUser }) => {
  const [dailyTasks, setDailyTasks] = useState<DailyTask[]>([]);
  const [gameTasks, setGameTasks] = useState<UserCampaign[]>([]);
  const [socialTasks, setSocialTasks] = useState<UserCampaign[]>([]);
  const [partnerTasks, setPartnerTasks] = useState<PartnerCampaign[]>([]);

  const [dailyTasksCompleted, setDailyTasksCompleted] = useState(false);

  

  const checkDailyCompletion = (tasks: DailyTask[]) => {
    const allMandatoryClaimed = tasks
      .filter(t => t.mandatory)
      .every(t => t.claimed);

    setDailyTasksCompleted(allMandatoryClaimed);
  };


  useEffect(() => {
    fetchDailyTasks().then(tasks => {
        setDailyTasks(tasks);
        checkDailyCompletion(tasks);
    });

    fetchUserCampaigns().then(campaigns => {
        setGameTasks(campaigns.filter(c => c.campaignType === 'Game'));
        setSocialTasks(campaigns.filter(c => c.campaignType === 'Social'));
    });

    fetchPartnerCampaigns().then(setPartnerTasks);
  }, []);




  const handleTaskSpinReward = async () => {
    const result = await completeTaskForSpin();
    if (result.success && result.user) {
        setUser(result.user);
        // Optionally show a small notification/toast here
    }
  };

  const processClaim = async (taskId: string) => {
    const result = await claimDailyTask(taskId);
    if (result.success && result.user) {
      setUser(result.user);
      const updatedTasks = dailyTasks.map(t => (t.id === taskId ? { ...t, claimed: true } : t));
      setDailyTasks(updatedTasks);
      checkDailyCompletion(updatedTasks);
    }
  };

  const handleClaim = async (taskId: string) => {
    const task = dailyTasks.find(t => t.id === taskId);
    if (!task || task.claimed) return;

    if (task.id === 'dt1') {
      try {
        await show_9692552();
        await processClaim(taskId);
      } catch (e) {
        console.error("Ad failed or was closed early:", e);
        alert("You must watch the entire ad to claim the reward.");
      }
      return;
    }

    if (task.action === 'share') {
      const referralLink = 'https://t.me/cashubux_bot?start=ref12345';
      const url = encodeURIComponent(referralLink);
      const text = encodeURIComponent("Join me on CashUBux Bot and earn crypto together!");
      const telegramUrl = `https://t.me/share/url?url=${url}&text=${text}`;
      window.open(telegramUrl, '_blank');
    }

    if (task.action === 'link' && task.link) {
      window.open(task.link, '_blank');
    }

    await processClaim(taskId);
  };






  
  return (
    <div className="space-y-8">
      <PromoCodeSection setUser={setUser} />
      
      <section>
        <h2 className="text-xl font-bold mb-4 text-white">Daily tasks</h2>
        <div className="space-y-3">
          {dailyTasks.map(task => (
            <DailyTaskItem key={task.id} task={task} onClaim={handleClaim} />
          ))}
        </div>
      </section>

      <div className="space-y-8 relative">
        {!dailyTasksCompleted && <TasksLockedOverlay />}
        <div className={`space-y-8 transition-opacity ${!dailyTasksCompleted ? 'opacity-20 pointer-events-none' : ''}`}>
            
            <section>
                <h2 className="text-xl font-bold mb-4 text-white">Game tasks</h2>
                <div className="space-y-3">
                    {gameTasks.length > 0 ? (
                        gameTasks.map(task => (
                            <CampaignTaskItem key={task.id} task={task} icon={ICONS.game} description="Play to earn" buttonClass="bg-purple-500 hover:bg-purple-600" onStart={handleTaskSpinReward} />
                        ))
                    ) : (
                        <div className="bg-slate-800 p-6 rounded-lg text-center text-slate-400">
                            <p>No game tasks available right now.</p>
                        </div>
                    )}
                </div>
            </section>
            
            <section>
                <h2 className="text-xl font-bold mb-4 text-white">Social tasks</h2>
                <div className="space-y-3">
                    {socialTasks.length > 0 ? (
                        socialTasks.map(task => (
                            <CampaignTaskItem key={task.id} task={task} icon={ICONS.telegram} description="Subscribe and react" buttonClass="bg-pink-500 hover:bg-pink-600" onStart={handleTaskSpinReward} />
                        ))
                    ) : (
                         <div className="bg-slate-800 p-6 rounded-lg text-center text-slate-400">
                            <p>No social tasks available right now.</p>
                            <p className="text-sm mt-1">Create one to get started!</p>
                        </div>
                    )}
                </div>
            </section>
            
            <section>
                <h2 className="text-xl font-bold mb-4 text-white">Partner tasks</h2>
                <div className="space-y-3">
                    {partnerTasks.length > 0 ? (
                        partnerTasks.map(task => (
                        <PartnerTaskItem key={task.id} task={task} onStart={handleTaskSpinReward} />
                        ))
                    ) : (
                        <div className="bg-slate-800 p-6 rounded-lg text-center text-slate-400">
                            <p>No partner tasks available right now.</p>
                            <p className="text-sm mt-1">Check back later!</p>
                        </div>
                    )}
                </div>
            </section>
        </div>
    </div>

    </div>
  );
};

export default EarningsPage;