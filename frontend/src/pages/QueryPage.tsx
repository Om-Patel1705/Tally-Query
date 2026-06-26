import { useState, useRef, useEffect } from 'react';
import { ArrowUp, Search, ChevronLeft, ChevronRight, Table2, Upload, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '../hooks/useQuery';
import { useSessionStore } from '../store/sessionStore';
import { clearSession, getSessionData } from '../api/client';
import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, Tooltip, ResponsiveContainer,
} from 'recharts';

interface QAPair {
  id: string;
  question: string;
  answer: string;
  chartData: { name: string; value: number }[] | null;
  chartType: 'bar' | 'line' | null;
  data: Record<string, any>[];  // Add data field
}

const SUGGESTIONS = [
  "Show sales for last month",
  "Top 5 customers",
  "Outstanding invoices",
  "Monthly sales trend",
];

export default function QueryPage() {
  const [input, setInput] = useState('');
  const [qaHistory, setQaHistory] = useState<QAPair[]>([]);
  const [showDatasetModal, setShowDatasetModal] = useState(false);
  const [datasetData, setDatasetData] = useState<Record<string, any>[] | null>(null);
  const [datasetPage, setDatasetPage] = useState(1);
  const [datasetPageSize] = useState(50);
  const [datasetTotalRows, setDatasetTotalRows] = useState(0);
  const [datasetTotalPages, setDatasetTotalPages] = useState(0);
  const [datasetColumns, setDatasetColumns] = useState<string[]>([]);
  const [isLoadingDataset, setIsLoadingDataset] = useState(false);
  const { query, isLoading, error } = useQuery();
  const { sessionId, fileName, clearSession: clearStoreSession } = useSessionStore();
  const navigate = useNavigate();
  const feedRef = useRef<HTMLDivElement>(null);
  const qaRefs = useRef<Record<string, HTMLDivElement | null>>({});

  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [qaHistory.length]);

  const handleUploadNew = async () => {
    if (sessionId) {
      try {
        await clearSession(sessionId);
      } catch (err) {
        console.error('Failed to clear session:', err);
      }
    }
    clearStoreSession();
    navigate('/');
  };

  const submitQuestion = async (q: string) => {
    const question = q.trim();
    if (!question) return;

    console.log('Submitting question:', question);
    const response = await query(question);
    console.log('Response from query hook:', response);
    
    if (response) {
      console.log('Processing response...');
      const id = crypto.randomUUID();
      
      // Determine chart type based on data
      let chartType: 'bar' | 'line' | null = null;
      if (response.chart_data) {
        console.log('Chart data exists:', response.chart_data);
        // Check if x-axis looks like dates/time-series
        const isTimeSeries = response.chart_data.labels.some(label => 
          /^\d{4}-\d{2}/.test(label) || 
          /^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)/i.test(label)
        );
        chartType = isTimeSeries ? 'line' : 'bar';
      }

      const chartData = response.chart_data
        ? response.chart_data.labels.map((label, i) => ({
            name: label,
            value: response.chart_data!.values[i],
          }))
        : null;

      console.log('Creating QA pair:', { id, question, answer: response.answer, chartData, chartType, data: response.data });
      
      setQaHistory(prev => {
        const updated = [...prev, {
          id,
          question,
          answer: response.answer,
          chartData,
          chartType,
          data: response.data || [],
        }];
        console.log('Updated QA history:', updated);
        return updated;
      });
      setInput('');
    } else {
      console.log('No response received');
    }
  };

  const scrollToQA = (id: string) => {
    setTimeout(() => {
      qaRefs.current[id]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 60);
  };

  const handleClearSession = async () => {
    if (sessionId) {
      try {
        await clearSession(sessionId);
      } catch (err) {
        console.error('Failed to clear session:', err);
      }
    }
    clearStoreSession();
    setQaHistory([]);
    setDatasetData(null);
    navigate('/');
  };

  const handleViewDataset = async () => {
    if (!sessionId) return;
    try {
      setIsLoadingDataset(true);
      setDatasetPage(1);
      const response = await getSessionData(sessionId, 1, datasetPageSize);
      setDatasetData(response.data);
      setDatasetTotalRows(response.total_rows);
      setDatasetTotalPages(response.total_pages);
      setDatasetColumns(response.columns);
      setShowDatasetModal(true);
    } catch (err) {
      console.error('Failed to load dataset:', err);
    } finally {
      setIsLoadingDataset(false);
    }
  };

  const handleDatasetPageChange = async (newPage: number) => {
    if (!sessionId) return;
    try {
      setIsLoadingDataset(true);
      const response = await getSessionData(sessionId, newPage, datasetPageSize);
      setDatasetData(response.data);
      setDatasetPage(newPage);
    } catch (err) {
      console.error('Failed to load dataset page:', err);
    } finally {
      setIsLoadingDataset(false);
    }
  };

  const handleChipClick = (suggestion: string) => {
    setInput(suggestion);
    submitQuestion(suggestion);
  };

  const scrollbarHide: React.CSSProperties = { scrollbarWidth: 'none' as any };

  return (
    <div
      className="flex h-screen bg-white overflow-hidden"
      style={{ fontFamily: "'Inter', system-ui, -apple-system, sans-serif" }}
    >
      {/* Sidebar */}
      <aside className="w-[280px] shrink-0 flex flex-col border-r border-[#E5E7EB] bg-[#FAFAFA] overflow-hidden">
        {/* Logo */}
        <div className="px-5 py-[14px] border-b border-[#E5E7EB] flex items-center gap-2.5 shrink-0">
          <div className="w-[18px] h-[18px] rounded-[4px] bg-[#2563EB] flex items-center justify-center shrink-0">
            <span className="text-white text-[9px] font-bold leading-none">T</span>
          </div>
          <span className="text-[13px] font-semibold text-[#111827] tracking-tight">TallyQuery</span>
        </div>

        {/* File Info */}
        <div className="px-4 pt-4 pb-3 shrink-0">
          <p className="text-[10px] font-semibold text-[#9CA3AF] uppercase tracking-widest mb-2.5">
            Data Source
          </p>

          {fileName ? (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5 bg-[#EFF6FF] border border-[#BFDBFE] rounded-full px-2.5 py-1 min-w-0 flex-1">
                <div className="w-1.5 h-1.5 rounded-full bg-[#2563EB] shrink-0" />
                <span className="text-[11px] text-[#1D4ED8] font-medium truncate">{fileName}</span>
              </div>
            </div>
          ) : (
            <button
              onClick={handleUploadNew}
              className="w-full text-center text-[11px] text-[#2563EB] hover:underline"
            >
              Upload a file
            </button>
          )}

          {fileName && (
            <>
              <button
                onClick={handleViewDataset}
                className="mt-3 w-full text-left text-[12px] px-2.5 py-1.5 rounded-md flex items-center gap-2 text-[#374151] hover:bg-[#F3F4F6] transition-colors duration-100"
              >
                <Table2 size={13} className="shrink-0" />
                View dataset
              </button>
              <button
                onClick={handleClearSession}
                className="mt-1 w-full text-left text-[12px] px-2.5 py-1.5 rounded-md flex items-center gap-2 text-[#374151] hover:bg-[#F3F4F6] transition-colors duration-100"
              >
                <Upload size={13} className="shrink-0" />
                Upload new file
              </button>
            </>
          )}
        </div>

        <div className="mx-4 border-t border-[#E5E7EB] shrink-0" />

        {/* History */}
        <div
          className="flex-1 overflow-y-auto px-4 pt-3 pb-4"
          style={scrollbarHide}
        >
          <p className="text-[10px] font-semibold text-[#9CA3AF] uppercase tracking-widest mb-2.5">
            History
          </p>
          {qaHistory.length === 0 ? (
            <p className="text-[12px] text-[#9CA3AF] leading-relaxed">
              Questions you ask will appear here.
            </p>
          ) : (
            <ul className="space-y-px">
              {qaHistory.map(qa => (
                <li key={qa.id}>
                  <button
                    onClick={() => scrollToQA(qa.id)}
                    className="w-full text-left text-[12px] text-[#374151] hover:text-[#111827] hover:bg-[#F3F4F6] rounded-[5px] px-2 py-1.5 truncate transition-colors duration-100"
                  >
                    {qa.question}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </aside>

      {/* Main Area */}
      <main className="flex-1 flex flex-col overflow-hidden bg-white">
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#E5E7EB] shrink-0 flex items-center justify-between">
          <div>
            <h2 className="text-[14px] font-semibold text-[#111827]">Query Your Data</h2>
            <p className="text-[12px] text-[#6B7280] mt-0.5">
              {fileName ? `Analyzing: ${fileName}` : 'No file uploaded'}
            </p>
          </div>
          {!fileName && (
            <button
              onClick={handleUploadNew}
              className="text-[12px] text-[#2563EB] hover:underline"
            >
              Upload a file
            </button>
          )}
        </div>

        {/* Q&A Feed */}
        <div
          ref={feedRef}
          className="flex-1 overflow-y-auto"
          style={scrollbarHide}
        >
          {qaHistory.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-6">
              <div className="w-9 h-9 rounded-lg bg-[#EFF6FF] flex items-center justify-center mb-3">
                <div className="w-5 h-5 rounded-[4px] bg-[#2563EB] flex items-center justify-center">
                  <span className="text-white text-[10px] font-bold leading-none">T</span>
                </div>
              </div>
              <p className="text-[14px] font-semibold text-[#111827] mb-1">
                Ask about your data
              </p>
              <p className="text-[13px] text-[#9CA3AF] max-w-[280px] leading-relaxed">
                Ask questions in natural language about your uploaded data.
              </p>
            </div>
          ) : (
            <div className="px-6 py-6 space-y-5">
              {qaHistory.map(qa => (
                <div
                  key={qa.id}
                  ref={el => { qaRefs.current[qa.id] = el; }}
                  className="space-y-2"
                >
                  {/* Question bubble */}
                  <div className="flex justify-end">
                    <div className="bg-[#2563EB] text-white text-[13px] rounded-lg rounded-tr-[4px] px-4 py-2.5 max-w-[68%] leading-relaxed">
                      {qa.question}
                    </div>
                  </div>

                  {/* Answer card */}
                  <div className="flex justify-start">
                    <div className="border border-[#E5E7EB] rounded-lg rounded-tl-[4px] px-4 py-3.5 max-w-[80%] min-w-[260px] bg-white">
                      <div className="text-[13px] text-[#111827] leading-relaxed whitespace-pre-wrap">
                        {qa.answer}
                      </div>
                      
                      {/* Data Table */}
                      {qa.data && qa.data.length > 0 && (
                        <div className="mt-3 overflow-x-auto">
                          <table className="text-[11px] w-full border-collapse">
                            <thead>
                              <tr className="border-b border-[#E5E7EB]">
                                {Object.keys(qa.data[0]).map(key => (
                                  <th key={key} className="text-left px-2 py-1 font-semibold text-[#374151] bg-[#F9FAFB]">
                                    {key}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {qa.data.map((row, idx) => (
                                <tr key={idx} className="border-b border-[#F3F4F6] hover:bg-[#F9FAFB]">
                                  {Object.values(row).map((value: any, vIdx) => (
                                    <td key={vIdx} className="px-2 py-1 text-[#6B7280]">
                                      {String(value).substring(0, 50)}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                      
                      {qa.chartData && qa.chartType && (
                        <div className="mt-3 h-[120px]">
                          <ResponsiveContainer width="100%" height="100%">
                            {qa.chartType === 'bar' ? (
                              <BarChart data={qa.chartData} margin={{ top: 4, right: 0, left: -18, bottom: 0 }}>
                                <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#9CA3AF' }} tickLine={false} axisLine={false} />
                                <YAxis tick={{ fontSize: 10, fill: '#9CA3AF' }} tickLine={false} axisLine={false}
                                  tickFormatter={(v: number) => {
                                    if (v >= 1000) return `${(v / 1000).toFixed(0)}k`;
                                    if (v >= 1000000) return `${(v / 1000000).toFixed(1)}M`;
                                    return v.toLocaleString();
                                  }} />
                                <Tooltip 
                                  contentStyle={{ border: '1px solid #E5E7EB', borderRadius: 6, fontSize: 11, boxShadow: 'none', padding: '4px 8px' }}
                                  cursor={{ fill: '#F9FAFB' }}
                                  formatter={(v: number) => [v.toLocaleString(), 'Value']}
                                />
                                <Bar dataKey="value" fill="#2563EB" radius={[3, 3, 0, 0]} />
                              </BarChart>
                            ) : (
                              <LineChart data={qa.chartData} margin={{ top: 4, right: 0, left: -18, bottom: 0 }}>
                                <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#9CA3AF' }} tickLine={false} axisLine={false} />
                                <YAxis tick={{ fontSize: 10, fill: '#9CA3AF' }} tickLine={false} axisLine={false}
                                  tickFormatter={(v: number) => {
                                    if (v >= 1000) return `${(v / 1000).toFixed(0)}k`;
                                    if (v >= 1000000) return `${(v / 1000000).toFixed(1)}M`;
                                    return v.toLocaleString();
                                  }} />
                                <Tooltip 
                                  contentStyle={{ border: '1px solid #E5E7EB', borderRadius: 6, fontSize: 11, boxShadow: 'none', padding: '4px 8px' }}
                                  formatter={(v: number) => [v.toLocaleString(), 'Value']}
                                />
                                <Line dataKey="value" stroke="#2563EB" strokeWidth={2} dot={{ r: 3, fill: '#2563EB' }} />
                              </LineChart>
                            )}
                          </ResponsiveContainer>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="border-t border-[#E5E7EB] bg-white px-6 py-4 shrink-0">
          {/* Suggestion chips */}
          <div className="flex gap-2 flex-wrap mb-3">
            {SUGGESTIONS.map(s => (
              <button
                key={s}
                onClick={() => handleChipClick(s)}
                className="text-[11px] text-[#374151] bg-[#F3F4F6] hover:bg-[#E5E7EB] border border-transparent rounded-full px-3 py-1 transition-colors duration-100 whitespace-nowrap"
              >
                {s}
              </button>
            ))}
          </div>

          {/* Error message */}
          {error && (
            <div className="mb-3 p-2 bg-[#FEE2E2] border border-[#FECACA] rounded">
              <p className="text-[11px] text-[#991B1B]">{error}</p>
            </div>
          )}

          {/* Input row */}
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submitQuestion(input); } }}
              placeholder="Ask about your sales, customers, invoices..."
              disabled={!sessionId || isLoading}
              className="flex-1 text-[13px] border border-[#E5E7EB] rounded-md px-3.5 py-2.5 placeholder:text-[#9CA3AF] text-[#111827] focus:outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#2563EB]/10 transition-colors bg-white disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button
              onClick={() => submitQuestion(input)}
              disabled={!input.trim() || isLoading || !sessionId}
              className="w-[38px] h-[38px] rounded-md bg-[#2563EB] hover:bg-[#1D4ED8] disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center transition-colors duration-100 shrink-0"
            >
              {isLoading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <ArrowUp size={15} className="text-white" />
              )}
            </button>
          </div>
        </div>
      </main>

      {/* Dataset Modal */}
      {showDatasetModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-6xl w-full max-h-[85vh] flex flex-col shadow-xl">
            <div className="px-5 py-4 border-b border-[#E5E7EB] flex items-center justify-between">
              <div>
                <h3 className="text-[15px] font-semibold text-[#111827]">Dataset Preview</h3>
                <p className="text-[12px] text-[#6B7280] mt-0.5">{datasetTotalRows.toLocaleString()} rows total</p>
              </div>
              <button
                onClick={() => setShowDatasetModal(false)}
                className="text-[#6B7280] hover:text-[#111827] p-1 hover:bg-[#F3F4F6] rounded transition-colors"
              >
                <X size={18} />
              </button>
            </div>
            
            <div className="flex-1 overflow-auto">
              {isLoadingDataset ? (
                <div className="flex items-center justify-center h-64">
                  <div className="w-6 h-6 border-2 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
                </div>
              ) : datasetData && datasetData.length > 0 ? (
                <div className="min-h-full">
                  <table className="text-[12px] w-full border-collapse">
                    <thead className="sticky top-0 bg-white z-10">
                      <tr className="border-b border-[#E5E7EB]">
                        {datasetColumns.map(col => (
                          <th key={col} className="text-left px-4 py-3 font-semibold text-[#374151] bg-[#F9FAFB] whitespace-nowrap border-b-2 border-[#E5E7EB]">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {datasetData.map((row, idx) => (
                        <tr key={idx} className="border-b border-[#F3F4F6] hover:bg-[#F9FAFB] transition-colors">
                          {datasetColumns.map(col => (
                            <td key={col} className="px-4 py-3 text-[#374151] whitespace-nowrap">
                              {String(row[col] ?? '')}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="flex items-center justify-center h-64">
                  <p className="text-[13px] text-[#9CA3AF]">No data available</p>
                </div>
              )}
            </div>
            
            {/* Pagination */}
            {datasetTotalPages > 1 && (
              <div className="px-5 py-3 border-t border-[#E5E7EB] flex items-center justify-between bg-[#F9FAFB] rounded-b-lg">
                <div className="text-[12px] text-[#6B7280]">
                  Page {datasetPage} of {datasetTotalPages}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleDatasetPageChange(datasetPage - 1)}
                    disabled={datasetPage === 1 || isLoadingDataset}
                    className="px-3 py-1.5 text-[12px] text-[#374151] bg-white border border-[#E5E7EB] rounded hover:bg-[#F3F4F6] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1 transition-colors"
                  >
                    <ChevronLeft size={14} />
                    Previous
                  </button>
                  <button
                    onClick={() => handleDatasetPageChange(datasetPage + 1)}
                    disabled={datasetPage === datasetTotalPages || isLoadingDataset}
                    className="px-3 py-1.5 text-[12px] text-[#374151] bg-white border border-[#E5E7EB] rounded hover:bg-[#F3F4F6] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1 transition-colors"
                  >
                    Next
                    <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
