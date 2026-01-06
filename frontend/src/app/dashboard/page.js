"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import { Upload, FileText, CheckCircle, X, LogOut, Zap, Calendar, TrendingUp, AlertCircle, Sparkles, History, Users, Clock, AlertTriangle } from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { uploadImage, predictRisk, fetchHistory } from '@/utils/api';

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [scanResult, setScanResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [showPopup, setShowPopup] = useState(false);
  
  // --- MASALA STATE ---
  const [popupData, setPopupData] = useState({ 
    daysToExam: '45', 
    subjectType: 'core', 
    semesterPhase: 'mid',
    facultyStrictness: 2, 
    isLab: false,
    hasProxy: false,
    bunkedLastClass: false,
    isFirstPeriod: false
  });

  useEffect(() => {
    const token = Cookies.get('token');
    if (!token) {
      router.push('/login');
      return;
    }
    setUser({ name: "Scholar" });
    loadHistory();
  }, [router]);

  const loadHistory = async () => {
    try {
      const data = await fetchHistory();
      // Ensure history doesn't break if API returns weird data
      setHistory(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Failed to load history");
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setScanResult(null);
    }
  };

  const handleScan = async () => {
    if (!file) {
      toast.error("Please upload a screenshot first");
      return;
    }
    setLoading(true);
    try {
      const data = await uploadImage(file);
      setScanResult(data);
      toast.success("Evidence Analyzed");
      setShowPopup(true);
    } catch (error) {
      toast.error("Scan Failed");
    } finally {
      setLoading(false);
    }
  };

  const handleFinalPrediction = async () => {
    try {
      const result = await predictRisk({
        overall_attendance: scanResult.extracted_data.overall_attendance,
        is_core_subject: popupData.subjectType === 'core' ? 1 : 0,
        days_to_exam: parseInt(popupData.daysToExam) || 30,
        semester_phase: popupData.semesterPhase === 'start' ? 0 : popupData.semesterPhase === 'mid' ? 1 : 2,
        faculty_strictness: parseInt(popupData.facultyStrictness),
        is_lab: popupData.isLab,
        has_proxy: popupData.hasProxy,
        bunked_last_class: popupData.bunkedLastClass,
        is_first_period: popupData.isFirstPeriod,
        filename: file.name
      });
      setScanResult(prev => ({ ...prev, ai_analysis: { ...result } }));
      toast.success("Fate Calculated");
    } catch (error) {
      // --- CRITICAL FIX: Handle Backend being in "Lite Mode" ---
      console.log("Prediction API failed (likely disabled on backend), using fallback UI");
      setScanResult(prev => ({
        ...prev,
        ai_analysis: {
            prediction: "Attendance Logged",
            confidence: "100%",
            message: "Prediction engine is offline in Lite Mode. Only OCR is active."
        }
      }));
      toast.success("Data Recorded (Lite Mode)");
    } finally {
      setShowPopup(false);
      loadHistory(); 
    }
  };

  // Helper variables for Safe Rendering
  const predictionText = scanResult?.ai_analysis?.prediction || "Pending...";
  const isSafe = predictionText.includes("Safe") || predictionText.includes("Logged");
  const chartData = [...history].reverse().map(item => ({
    date: new Date(item.timestamp).toLocaleString('en-US', {
      month: 'short', day: 'numeric', hour: 'numeric', minute: 'numeric', hour12: true
    }),
    attendance: item.overall_attendance
  }));

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 text-white font-sans selection:bg-cyan-500/30">
      <Toaster toastOptions={{ style: { background: '#1e293b', color: '#fff' } }}/>
      <div className="relative z-10 px-6 py-8 max-w-7xl mx-auto">
        
        {/* Header */}
        <header className="flex justify-between items-center mb-12">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">Should I Bunk?</h1>
              <p className="text-xs text-slate-400">Context-Aware AI Advisor</p>
            </div>
          </div>
          <button onClick={() => { Cookies.remove('token'); router.push('/login'); }} className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 transition text-sm">
            <LogOut size={16} className="text-red-400"/> Logout
          </button>
        </header>

        <div className="grid lg:grid-cols-2 gap-8 mb-8">
           {/* Upload Card */}
           <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl h-fit hover:border-cyan-500/30 transition-all duration-300">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 rounded-xl bg-cyan-500/10 text-cyan-400"><Upload size={20}/></div>
              <h2 className="text-lg font-bold">Upload Screenshot</h2>
            </div>
            <label className={`block border-2 border-dashed rounded-2xl p-10 mb-6 cursor-pointer transition-all ${file ? 'border-cyan-500/50 bg-cyan-500/5' : 'border-white/10 hover:border-cyan-500/30'}`}>
              <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
              <div className="flex flex-col items-center text-center">
                {file ? <CheckCircle className="w-12 h-12 text-cyan-400 mb-2"/> : <FileText className="w-12 h-12 text-slate-600 mb-2"/>}
                <span className="font-medium text-slate-300">{file ? file.name : "Click to Upload"}</span>
              </div>
            </label>
            <button onClick={handleScan} disabled={loading} className="w-full bg-gradient-to-r from-cyan-400 to-blue-500 text-white font-bold py-4 rounded-xl hover:shadow-lg hover:shadow-cyan-500/50 transition-all flex items-center justify-center gap-2 disabled:opacity-50">
              {loading ? "Scanning..." : <><Zap size={20}/> Analyze Risk</>}
            </button>
          </div>

          {/* Verdict Card */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl min-h-[400px] flex flex-col">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 rounded-xl bg-blue-500/10 text-blue-400"><TrendingUp size={20}/></div>
              <h2 className="text-lg font-bold">AI Verdict</h2>
            </div>
            {scanResult ? (
              <div className="flex-1 flex flex-col justify-center animate-in fade-in zoom-in duration-300">
                <div className="text-center mb-8">
                  <div className="text-6xl font-black text-white mb-2">{scanResult.extracted_data.overall_attendance}%</div>
                  <div className="text-xs text-slate-400 uppercase tracking-widest">Attendance Detected</div>
                </div>

                {/* --- CRITICAL FIX: Safe Render Check --- */}
                {scanResult.ai_analysis ? (
                   <div className={`p-6 rounded-2xl border backdrop-blur-sm ${isSafe ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-red-500/10 border-red-500/30'}`}>
                    <div className="flex items-start gap-4">
                      {isSafe ? <CheckCircle className="text-emerald-400 mt-1 flex-shrink-0"/> : <AlertCircle className="text-red-400 mt-1 flex-shrink-0"/>}
                      <div>
                        <h3 className={`text-xl font-bold mb-1 ${isSafe ? 'text-emerald-400' : 'text-red-400'}`}>
                          {predictionText}
                        </h3>
                        <p className="text-sm text-slate-300 leading-relaxed">{scanResult.ai_analysis.message || "Data extracted successfully."}</p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-slate-400 p-4 border border-white/10 rounded-xl bg-white/5">
                    <p>Analysis pending input...</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-slate-500">
                <Zap size={48} className="mb-4 opacity-20"/>
                <p>Waiting for data...</p>
              </div>
            )}
          </div>
        </div>

        {/* Chart Section */}
        {history.length > 1 && (
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl mb-8">
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorAtt" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                  <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '12px', color: '#fff' }} />
                  <Area type="monotone" dataKey="attendance" stroke="#22d3ee" strokeWidth={3} fillOpacity={1} fill="url(#colorAtt)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* History Grid */}
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {history.map((log) => {
              // Safety check for history prediction strings
              const logPrediction = log.prediction || "Logged";
              const logIsSafe = logPrediction.includes("Safe") || logPrediction.includes("Logged");
              return (
                <div key={log._id} className="bg-black/20 p-4 rounded-xl border border-white/5">
                  <div className="flex justify-between mb-2">
                    <span className="text-xs text-slate-500">{new Date(log.timestamp).toLocaleDateString()}</span>
                    <span className={`text-xs font-bold px-2 py-1 rounded ${logIsSafe ? 'text-emerald-400 bg-emerald-500/10' : 'text-red-400 bg-red-500/10'}`}>{logPrediction}</span>
                  </div>
                  <div className="text-xl font-bold">{log.overall_attendance}%</div>
                  <div className="text-xs text-slate-500 truncate">{log.filename}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* --- MASALA POPUP --- */}
        {showPopup && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in zoom-in duration-200">
            <div className="bg-slate-900 border border-white/10 w-full max-w-lg rounded-3xl p-6 shadow-2xl relative max-h-[90vh] overflow-y-auto">
              <button onClick={() => setShowPopup(false)} className="absolute top-4 right-4 text-slate-500 hover:text-white"><X size={20}/></button>
              
              <h3 className="text-xl font-bold text-white mb-1">Context Check 🧠</h3>
              <p className="text-sm text-slate-400 mb-6">Let's look at the B.Tech Reality.</p>

              <div className="space-y-4">
                
                {/* 1. Basic Stats */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-bold text-slate-500 uppercase mb-2 block">Days to Exam</label>
                    <input type="number" className="w-full bg-white/5 border border-white/10 rounded-xl py-3 px-4 text-white focus:border-cyan-500 outline-none" value={popupData.daysToExam} onChange={(e) => setPopupData({...popupData, daysToExam: e.target.value})}/>
                  </div>
                  <div>
                    <label className="text-xs font-bold text-slate-500 uppercase mb-2 block">Strictness</label>
                    <div className="flex bg-white/5 rounded-xl border border-white/10 overflow-hidden">
                      {[1, 2, 3].map(v => (
                        <button key={v} onClick={() => setPopupData({...popupData, facultyStrictness: v})} className={`flex-1 py-3 text-xs font-bold transition ${popupData.facultyStrictness === v ? 'bg-cyan-500 text-black' : 'text-slate-400 hover:bg-white/10'}`}>
                          {v === 1 ? 'Chill' : v === 2 ? 'Mid' : 'Strict'}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* 2. THE MASALA TOGGLES */}
                <div className="space-y-3 pt-2">
                  <div onClick={() => setPopupData({...popupData, isLab: !popupData.isLab})} className={`flex items-center justify-between p-4 rounded-xl border cursor-pointer transition ${popupData.isLab ? 'bg-purple-500/20 border-purple-500' : 'bg-white/5 border-white/10 hover:border-white/20'}`}>
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${popupData.isLab ? 'bg-purple-500 text-white' : 'bg-white/10 text-slate-400'}`}><Sparkles size={18}/></div>
                      <span className={popupData.isLab ? 'text-white font-bold' : 'text-slate-300'}>It's a Lab</span>
                    </div>
                    {popupData.isLab && <CheckCircle size={18} className="text-purple-400"/>}
                  </div>

                  <div onClick={() => setPopupData({...popupData, hasProxy: !popupData.hasProxy})} className={`flex items-center justify-between p-4 rounded-xl border cursor-pointer transition ${popupData.hasProxy ? 'bg-emerald-500/20 border-emerald-500' : 'bg-white/5 border-white/10 hover:border-white/20'}`}>
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${popupData.hasProxy ? 'bg-emerald-500 text-white' : 'bg-white/10 text-slate-400'}`}><Users size={18}/></div>
                      <div>
                        <div className={popupData.hasProxy ? 'text-white font-bold' : 'text-slate-300'}>Proxy Available</div>
                        <div className="text-xs text-slate-500">I have a friend inside</div>
                      </div>
                    </div>
                    {popupData.hasProxy && <CheckCircle size={18} className="text-emerald-400"/>}
                  </div>

                  <div onClick={() => setPopupData({...popupData, bunkedLastClass: !popupData.bunkedLastClass})} className={`flex items-center justify-between p-4 rounded-xl border cursor-pointer transition ${popupData.bunkedLastClass ? 'bg-red-500/20 border-red-500' : 'bg-white/5 border-white/10 hover:border-white/20'}`}>
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${popupData.bunkedLastClass ? 'bg-red-500 text-white' : 'bg-white/10 text-slate-400'}`}><AlertTriangle size={18}/></div>
                      <div>
                        <div className={popupData.bunkedLastClass ? 'text-white font-bold' : 'text-slate-300'}>Bunked Last Class</div>
                        <div className="text-xs text-slate-500">Teacher might remember me</div>
                      </div>
                    </div>
                    {popupData.bunkedLastClass && <CheckCircle size={18} className="text-red-400"/>}
                  </div>

                   <div onClick={() => setPopupData({...popupData, isFirstPeriod: !popupData.isFirstPeriod})} className={`flex items-center justify-between p-4 rounded-xl border cursor-pointer transition ${popupData.isFirstPeriod ? 'bg-blue-500/20 border-blue-500' : 'bg-white/5 border-white/10 hover:border-white/20'}`}>
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${popupData.isFirstPeriod ? 'bg-blue-500 text-white' : 'bg-white/10 text-slate-400'}`}><Clock size={18}/></div>
                      <span className={popupData.isFirstPeriod ? 'text-white font-bold' : 'text-slate-300'}>First Period (Sleepy)</span>
                    </div>
                    {popupData.isFirstPeriod && <CheckCircle size={18} className="text-blue-400"/>}
                  </div>
                </div>

                <button onClick={handleFinalPrediction} className="w-full bg-cyan-500 hover:bg-cyan-400 text-black font-bold py-4 rounded-xl mt-4 transition-all shadow-lg shadow-cyan-500/20">
                  Calculate Fate
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}