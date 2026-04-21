import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Send, User, Bot } from 'lucide-react';

import axios from 'axios';

export default function ChatInterface() {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Hello! I\'m your Finance AI Agent. Ask me anything about your spending, upload a PDF statement, or let\'s simulate a scenario like "Can I afford a ₹50,000 laptop?"' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userText = input;
    setMessages(prev => [...prev, { role: 'user', text: userText }]);
    setInput('');
    setLoading(true);
    
    try {
      const response = await axios.post('http://localhost:8000/chat', {
        query: userText,
        context: { "savings": 18000 } // Dummy context for now
      });
      
      const { insight, reason, recommendation } = response.data;
      const aiText = `**Insight:** ${insight}\n\n**Reason:** ${reason}\n\n**Recommendation:** ${recommendation}`;
      
      setMessages(prev => [...prev, { role: 'assistant', text: aiText }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', text: "Sorry, I couldn't reach the backend API. Is it running on port 8000?" }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass rounded-2xl h-[70vh] flex flex-col overflow-hidden shadow-2xl">
      <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
        {messages.map((msg, i) => (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            key={i} 
            className={`flex gap-4 max-w-[80%] ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
          >
            <div className={`h-10 w-10 shrink-0 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-indigo-500' : 'bg-[#2a2a35]'}`}>
              {msg.role === 'user' ? <User size={18} /> : <Bot size={18} className="text-indigo-400" />}
            </div>
            <div className={`p-4 rounded-2xl text-sm leading-relaxed ${msg.role === 'user' ? 'bg-indigo-500 text-white rounded-tr-none' : 'bg-white/5 border border-white/10 rounded-tl-none'}`}>
              {msg.text}
            </div>
          </motion.div>
        ))}
      </div>
      
      <div className="p-4 border-t border-white/5 bg-[#141419]">
        <div className="flex items-center gap-3 bg-white/5 p-2 rounded-xl border border-white/10 focus-within:border-indigo-500/50 transition-colors">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about your financial insights..."
            className="flex-1 bg-transparent border-none outline-none text-sm px-3 placeholder-gray-500"
          />
          <button onClick={handleSend} className="bg-indigo-500 hover:bg-indigo-600 p-2 rounded-lg text-white transition-colors">
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
