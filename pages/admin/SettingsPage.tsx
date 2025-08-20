import React, { useState, useEffect } from 'react';
import type { AdNetwork } from '../../types';
import { fetchSettings, updateSettings } from '../../services/api';

const SettingsPage: React.FC = () => {
    const [settings, setSettingsData] = useState<{ autoWithdrawals: boolean; adNetworks: AdNetwork[] } | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchSettings().then(data => {
            setSettingsData({
                autoWithdrawals: data.autoWithdrawals,
                adNetworks: data.adNetworks,
            });
            setLoading(false);
        });
    }, []);

    const handleSettingChange = async (key: 'autoWithdrawals', value: boolean) => {
        if (!settings) return;
        const newSettings = { ...settings, [key]: value };
        setSettingsData(newSettings); // Optimistic update
        const result = await updateSettings({ [key]: value });
        if (!result.success) {
            alert('Failed to save settings. Reverting.');
            // Revert on failure
            fetchSettings().then(data => setSettingsData(data));
        }
    };

    const handleAdNetworkToggle = async (networkId: string) => {
        if (!settings) return;
        const updatedNetworks = settings.adNetworks.map(n => 
            n.id === networkId ? { ...n, enabled: !n.enabled } : n
        );
        setSettingsData({ ...settings, adNetworks: updatedNetworks }); // Optimistic
        await updateSettings({ adNetworks: updatedNetworks });
    };

    const handleAddAdNetwork = async (name: string, code: string) => {
        if (!settings || !name || !code) return;
        const newNetwork: AdNetwork = {
            id: name.toLowerCase().replace(/\s/g, ''),
            name,
            code,
            enabled: true,
        };
        const updatedNetworks = [...settings.adNetworks, newNetwork];
        setSettingsData({ ...settings, adNetworks: updatedNetworks });
        await updateSettings({ adNetworks: updatedNetworks });
    };

    if (loading) {
        return <div className="text-center text-slate-400">Loading settings...</div>;
    }

    if (!settings) {
        return <div className="text-center text-red-500">Failed to load settings.</div>;
    }

    return (
        <div>
            <h1 className="text-4xl font-bold text-white mb-8">Application Settings</h1>

            <div className="space-y-12">
                {/* Withdrawal Settings */}
                <section className="bg-slate-800 p-6 rounded-xl border border-slate-700">
                    <h2 className="text-2xl font-bold mb-4">Withdrawal Settings</h2>
                    <div className="flex items-center justify-between">
                        <p className="text-slate-300">Enable automatic payouts for users?</p>
                        <button
                            onClick={() => handleSettingChange('autoWithdrawals', !settings.autoWithdrawals)}
                            className={`relative inline-flex items-center h-6 rounded-full w-11 transition-colors ${settings.autoWithdrawals ? 'bg-green-600' : 'bg-slate-600'}`}
                        >
                            <span className={`inline-block w-4 h-4 transform bg-white rounded-full transition-transform ${settings.autoWithdrawals ? 'translate-x-6' : 'translate-x-1'}`}/>
                        </button>
                    </div>
                     <p className="text-xs text-slate-500 mt-2">If disabled, all withdrawal requests will require manual approval.</p>
                </section>

                {/* Ad Network Settings */}
                <section className="bg-slate-800 p-6 rounded-xl border border-slate-700">
                    <h2 className="text-2xl font-bold mb-4">Ad Network Management</h2>
                     <div className="space-y-3 mb-6">
                        {settings.adNetworks.map(network => (
                            <div key={network.id} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                                <div>
                                    <p className="font-semibold">{network.name}</p>
                                    <p className="text-xs text-slate-400 font-mono truncate max-w-xs">{network.code}</p>
                                </div>
                                <button
                                    onClick={() => handleAdNetworkToggle(network.id)}
                                    className={`relative inline-flex items-center h-6 rounded-full w-11 transition-colors ${network.enabled ? 'bg-green-600' : 'bg-slate-600'}`}
                                >
                                    <span className={`inline-block w-4 h-4 transform bg-white rounded-full transition-transform ${network.enabled ? 'translate-x-6' : 'translate-x-1'}`}/>
                                </button>
                            </div>
                        ))}
                    </div>
                    <AddNetworkForm onAdd={handleAddAdNetwork} />
                </section>
            </div>
        </div>
    );
};

const AddNetworkForm: React.FC<{onAdd: (name: string, code: string) => void}> = ({ onAdd }) => {
    const [name, setName] = useState('');
    const [code, setCode] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onAdd(name, code);
        setName('');
        setCode('');
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4 pt-4 border-t border-slate-700">
            <h3 className="font-semibold">Add New Ad Network</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <input
                    type="text"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    placeholder="Network Name (e.g., AdCompany)"
                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg"
                    required
                />
                 <input
                    type="text"
                    value={code}
                    onChange={e => setCode(e.target.value)}
                    placeholder="Ad Script/Code Snippet"
                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg col-span-2"
                    required
                />
            </div>
            <button type="submit" className="bg-blue-500 text-white font-bold py-2 px-5 rounded-lg hover:bg-blue-600 transition-colors">
                + Add Network
            </button>
        </form>
    );
};

export default SettingsPage;
