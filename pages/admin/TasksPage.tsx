import React, { useState } from 'react';
import { createAdminTask } from '../../services/api';

const TasksPage: React.FC = () => {
    const [formData, setFormData] = useState({
        title: '',
        reward: '',
        category: 'Social' as 'Daily' | 'Game' | 'Social' | 'Partner',
    });
    const [isLoading, setIsLoading] = useState(false);
    const [feedback, setFeedback] = useState<{ message: string, isError: boolean } | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setFeedback(null);
        
        try {
            const result = await createAdminTask({
                title: formData.title,
                reward: parseInt(formData.reward, 10),
                category: formData.category,
            });

            if (result.success) {
                setFeedback({ message: 'Task created successfully!', isError: false });
                setFormData({ title: '', reward: '', category: 'Social' }); // Reset form
            } else {
                 setFeedback({ message: 'Failed to create task.', isError: true });
            }
        } catch (error) {
            setFeedback({ message: 'An error occurred.', isError: true });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <h1 className="text-4xl font-bold text-white mb-8">Add New Task</h1>

            <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 max-w-2xl mx-auto">
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label htmlFor="title" className="block text-sm font-medium text-slate-300 mb-2">Task Title</label>
                        <input
                            id="title"
                            type="text"
                            required
                            value={formData.title}
                            onChange={e => setFormData({ ...formData, title: e.target.value })}
                            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg"
                            placeholder="e.g., Subscribe to Awesome Channel"
                        />
                    </div>

                    <div>
                        <label htmlFor="reward" className="block text-sm font-medium text-slate-300 mb-2">Coin Reward</label>
                        <input
                            id="reward"
                            type="number"
                            required
                            value={formData.reward}
                            onChange={e => setFormData({ ...formData, reward: e.target.value })}
                            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg"
                            placeholder="e.g., 5000"
                        />
                    </div>
                    
                    <div>
                        <label htmlFor="category" className="block text-sm font-medium text-slate-300 mb-2">Task Category</label>
                        <select
                            id="category"
                            value={formData.category}
                            onChange={e => setFormData({ ...formData, category: e.target.value as any })}
                            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg"
                        >
                            <option value="Daily">Daily Task</option>
                            <option value="Game">Game Task</option>
                            <option value="Social">Social Task</option>
                            <option value="Partner">Partner Task</option>
                        </select>
                        <p className="text-xs text-slate-400 mt-1">This determines where the task will appear in the user app.</p>
                    </div>

                    <div className="pt-2">
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-green-500 text-white font-bold py-3 px-5 rounded-lg hover:bg-green-600 transition-colors disabled:bg-slate-600"
                        >
                            {isLoading ? 'Creating...' : 'Create Task'}
                        </button>
                    </div>

                    {feedback && (
                        <p className={`text-sm text-center font-semibold pt-2 ${feedback.isError ? 'text-red-500' : 'text-green-500'}`}>
                            {feedback.message}
                        </p>
                    )}
                </form>
            </div>
        </div>
    );
};

export default TasksPage;
