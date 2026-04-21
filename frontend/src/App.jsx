import React, { useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { UploadCloud, PieChart, MessageSquare, DollarSign, Lock } from 'lucide-react';
import TransactionGraph from './components/TransactionGraph';
import ChatInterface from './components/ChatInterface';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [uploadStatus, setUploadStatus] = useState(null);
  const [globalSavings, setGlobalSavings] = useState(0);
  const [pdfPassword, setPdfPassword] = useState('');
  const [pendingFile, setPendingFile] = useState(null);      // file waiting for password
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [modalPassword, setModalPassword] = useState('');

  React.useEffect(() => {
    axios.get('http://localhost:8000/summary')
      .then(res => {
        if (res.data && res.data.total_savings !== undefined) {
          setGlobalSavings(res.data.total_savings);
        }
      })
      .catch(err => console.error(err));
  }, [activeTab]);

  const handleFileUpload = async (file, password = '') => {
    if (!file) return;
    setUploadStatus({ type: 'loading', message: `Sending "${file.name}"... please wait.` });
    try {
      const formData = new FormData(); 
      formData.append('file', file);
      if (password) formData.append('password', password);
      const res = await axios.post('http://localhost:8000/upload/statement', formData);

      // If backend says 'encrypted', show the password popup automatically
      if (res.data.status === 'encrypted') {
        setPendingFile(file);
        setShowPasswordModal(true);
        setUploadStatus({ type: 'loading', message: '🔒 PDF is password-protected. Enter password in the popup.' });
        return;
      }

      setUploadStatus({ type: 'success', message: `✅ SUCCESS! ${res.data.message}` });
    } catch (err) {
      setUploadStatus({ type: 'error', message: `❌ Upload Failed: ${err.message}. Ensure backend is running.` });
    }
  };

  const handlePasswordSubmit = async () => {
    setShowPasswordModal(false);
    await handleFileUpload(pendingFile, modalPassword);
    setModalPassword('');
    setPendingFile(null);
  };

  return (
    <div className="min-h-screen bg-[#0f0f13] text-white font-sans flex flex-col md:flex-row">
      
      {/* Sidebar */}
      <motion.aside 
        initial={{ x: -100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        className="w-full md:w-64 glass border-r border-[#ffffff10] p-6 flex flex-col gap-8"
      >
        <div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-500 bg-clip-text text-transparent">
            Finance AI
          </h1>
          <p className="text-sm text-gray-400 mt-1">Intelligent Advisor</p>
        </div>

        <nav className="flex flex-col gap-2">
          <NavItem active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} icon={<PieChart size={20}/>} label="Dashboard" />
          <NavItem active={activeTab === 'chat'} onClick={() => setActiveTab('chat')} icon={<MessageSquare size={20}/>} label="Agent Chat" />
          <NavItem active={activeTab === 'upload'} onClick={() => {setActiveTab('upload'); setUploadStatus(null);}} icon={<UploadCloud size={20}/>} label="Upload Files" />
        </nav>
      </motion.aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-y-auto">
        <motion.header 
          initial={{ y: -20, opacity: 0 }} 
          animate={{ y: 0, opacity: 1 }}
          className="flex justify-between items-center mb-8"
        >
          <h2 className="text-3xl font-semibold capitalize">{activeTab}</h2>
          <div className="glass px-4 py-2 rounded-full flex items-center gap-2">
            <DollarSign size={16} className="text-green-400" />
            <span className="font-medium">Total Savings: ₹{globalSavings.toLocaleString()}</span>
          </div>
        </motion.header>

        {/* Tab Routing */}
        <motion.div
           key={activeTab}
           initial={{ opacity: 0, scale: 0.98 }}
           animate={{ opacity: 1, scale: 1 }}
           transition={{ duration: 0.3 }}
        >
          {activeTab === 'dashboard' && <TransactionGraph />}
          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'upload' && (
             <div 
               onDragOver={(e) => e.preventDefault()}
               onDrop={(e) => {
                 e.preventDefault();
                 const files = e.dataTransfer.files;
                 if (files && files.length > 0) {
                   handleFileUpload(files[0]);
                 }
               }}
               onClick={() => document.getElementById('fileUpload').click()}
               className="glass p-12 rounded-2xl flex flex-col items-center justify-center border-dashed border-2 border-indigo-500/30 hover:border-indigo-500/60 hover:bg-white/5 transition-all cursor-pointer relative"
             >
               <input 
                 id="fileUpload" 
                 type="file" 
                 className="hidden" 
                 onChange={(e) => {
                   if (e.target.files && e.target.files.length > 0) {
                     handleFileUpload(e.target.files[0]);
                   }
                 }} 
               />
               <UploadCloud size={64} className="text-indigo-400 mb-4" />
               <h3 className="text-xl font-medium mb-2">Upload Bank Statements or GPay Graphs</h3>
               <p className="text-gray-400 text-center max-w-md mb-4">Drag & drop your PDF or image files anywhere in this box, or click to browse files.</p>
               
               {/* Password Input for protected PDFs */}
               <div
                 className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-xl px-4 py-2 mb-4 w-full max-w-xs"
                 onClick={(e) => e.stopPropagation()}
               >
                 <Lock size={16} className="text-gray-400 shrink-0" />
                 <input
                   type="password"
                   placeholder="PDF password (if protected)"
                   value={pdfPassword}
                   onChange={(e) => setPdfPassword(e.target.value)}
                   className="bg-transparent outline-none text-sm text-white placeholder-gray-500 w-full"
                 />
               </div>
               
               {uploadStatus && (
                 <div className={`mt-2 px-6 py-3 rounded-xl border font-medium ${
                   uploadStatus.type === 'loading' ? 'bg-blue-500/20 border-blue-500/50 text-blue-300' :
                   uploadStatus.type === 'success' ? 'bg-green-500/20 border-green-500/50 text-green-300' :
                   'bg-red-500/20 border-red-500/50 text-red-300'
                 }`}>
                    {uploadStatus.message}
                 </div>
               )}
             </div>
          )}
        </motion.div>
      </main>

      {/* 🔒 Password Modal — appears automatically when PDF is encrypted */}
      {showPasswordModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="glass rounded-2xl p-8 w-full max-w-md shadow-2xl border border-indigo-500/30"
          >
            <div className="flex items-center gap-3 mb-2">
              <Lock size={24} className="text-indigo-400" />
              <h3 className="text-xl font-semibold">Password Required</h3>
            </div>
            <p className="text-gray-400 text-sm mb-6">
              This PDF is password-protected. Enter the password (usually your date of birth e.g. <span className="text-indigo-300">01011999</span> or PAN number).
            </p>
            <input
              type="password"
              autoFocus
              placeholder="Enter PDF password..."
              value={modalPassword}
              onChange={(e) => setModalPassword(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handlePasswordSubmit()}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 outline-none focus:border-indigo-500/60 transition-colors mb-4"
            />
            <div className="flex gap-3">
              <button
                onClick={handlePasswordSubmit}
                className="flex-1 bg-indigo-500 hover:bg-indigo-600 py-3 rounded-xl font-medium transition-colors"
              >
                🔓 Unlock & Parse
              </button>
              <button
                onClick={() => { setShowPasswordModal(false); setUploadStatus(null); }}
                className="px-6 py-3 rounded-xl border border-white/10 hover:bg-white/5 text-gray-400 transition-colors"
              >
                Cancel
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}

function NavItem({ icon, label, active, onClick }) {
  return (
    <button 
      onClick={onClick}
      className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${active ? 'bg-indigo-500/20 text-indigo-300' : 'hover:bg-white/5 text-gray-300 hover:text-white'}`}
    >
      {icon}
      <span className="font-medium">{label}</span>
    </button>
  );
}

export default App;
