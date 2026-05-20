import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  PieChart, Pie, Cell, Tooltip,
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer,
  LineChart, Line, CartesianGrid
} from 'recharts'

const MOCK_CATEGORY = [
  { name: '식비',      value: 37, color: '#1e73be' },
  { name: '쇼핑',      value: 20, color: '#38BDF8' },
  { name: '교통',      value: 24, color: '#60a5fa' },
  { name: '문화/여가', value: 4,  color: '#93c5fd' },
  { name: '편의/마트', value: 15, color: '#bfdbfe' },
]

const MOCK_TOP3 = [
  { name: '식비',  amount: 19500 },
  { name: '쇼핑',  amount: 10400 },
  { name: '교통',  amount: 12800 },
]

const MOCK_WEEKLY = [
  { week: '1주', 식비: 4200, 쇼핑: 1800 },
  { week: '2주', 식비: 5100, 쇼핑: 3200 },
  { week: '3주', 식비: 3800, 쇼핑: 2100 },
  { week: '4주', 식비: 6400, 쇼핑: 3300 },
]

const MOCK_TIME = [
  { label: '새벽', pct: 5,  icon: '🌙' },
  { label: '아침', pct: 20, icon: '🌅' },
  { label: '점심', pct: 40, icon: '☀️' },
  { label: '저녁', pct: 30, icon: '🍽️' },
  { label: '심야', pct: 5,  icon: '🌃' },
]

const MOCK_PRODUCTS = [
  {
    id: 1,
    tag: '💳 추천 카드',
    name: '하나 트래블로그 카드',
    desc: '지난달 대비 식비 지출이 높아요. 이 카드를 사용하면 더 많은 혜택을 받을 수 있어요.',
  },
  {
    id: 2,
    tag: '💰 추천 상품',
    name: 'OO 적금 상품',
    desc: '이 경우 OO카드를 사용하는데 이 카드를 사용하는 이 혜택을 많이 받아요.',
  },
]

const API_BASE = 'http://localhost:8000'

export default function Report() {
  const navigate = useNavigate()
  const [lifecycle, setLifecycle] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchLifecycle = async () => {
      try {
        setLoading(true)
        const res = await fetch(`${API_BASE}/api/lifecycle`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: 1,
            age: 28,
            monthly_spend: 527000,
            top_category: '식비',
          }),
        })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()
        setLifecycle(data)
      } catch (e) {
        setError(e.message)
        // 에러 시 목업으로 폴백
        setLifecycle({
          lifecycle_stage: '사회초년생',
          description: '소비 패턴 분석 결과, 외식·교통 지출이 많은 활동적인 사회초년생 단계예요.',
        })
      } finally {
        setLoading(false)
      }
    }
    fetchLifecycle()
  }, [])

  return (
    <div className="flex flex-col gap-4 pt-4 px-4 pb-24 overflow-y-auto">

      {/* 페르소나 배너 */}
      <div className="rounded-2xl bg-[#1e73be] text-white p-4 flex items-center gap-3">
        <div className="w-14 h-14 rounded-full bg-white/20 flex items-center justify-center text-2xl shrink-0">
          🐝
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs text-blue-100 mb-0.5">나의 소비 페르소나</p>
          <p className="font-bold text-base leading-tight">야행성 도시 탐험가</p>
          <p className="text-xs text-blue-100 mt-0.5 truncate">밤 점심, 저녁 외식 비중이 높고, 주로 도심에서</p>
        </div>
      </div>

      {/* 이번 달 총 소비 */}
      <div className="rounded-2xl border border-gray-100 p-4 shadow-sm">
        <p className="text-xs text-gray-400 mb-1">📊 2026년 5월 소비 리포트</p>
        <div className="flex items-end gap-2">
          <span className="text-2xl font-extrabold text-gray-900">52,700원</span>
          <span className="text-xs text-red-400 mb-1">지난달 대비 13% 증가 ↑</span>
        </div>
        <div className="flex gap-3 mt-3">
          {[['결제 건수', '10건'], ['결제 일수', '8일'], ['기타정보', '-']].map(([label, val]) => (
            <div key={label} className="flex-1 rounded-xl bg-gray-50 p-2 text-center">
              <p className="text-[10px] text-gray-400">{label}</p>
              <p className="text-sm font-bold text-gray-800">{val}</p>
            </div>
          ))}
        </div>
      </div>

      {/* 금융상품 추천 */}
      <div className="flex flex-col gap-2">
        <p className="text-xs text-gray-500 font-semibold">🤖 AI 상품 추천</p>
        {MOCK_PRODUCTS.map((p) => (
          <div key={p.id} className="rounded-2xl border border-gray-100 p-4 shadow-sm">
            <span className="text-[10px] bg-blue-100 text-[#1e73be] rounded-full px-2 py-0.5 font-semibold">
              {p.tag}
            </span>
            <p className="font-bold text-gray-800 text-sm mt-2">{p.name}</p>
            <p className="text-xs text-gray-500 mt-1 leading-relaxed">{p.desc}</p>
          </div>
        ))}
      </div>

      {/* 생애주기 - FastAPI 연결 */}
      <div className="rounded-2xl border border-blue-100 bg-blue-50 p-4">
        <p className="text-xs text-[#1e73be] font-semibold mb-2">🧬 AI 생애주기 분석</p>
        {loading ? (
          <div className="flex items-center gap-2 text-sm text-[#1e73be]">
            <span className="animate-spin">⏳</span> 분석 중...
          </div>
        ) : (
          <>
            <p className="font-bold text-[#1e73be] text-base">{lifecycle?.lifecycle_stage}</p>
            <p className="text-xs text-blue-400 mt-1 leading-relaxed">{lifecycle?.description}</p>
            {error && <p className="text-[10px] text-red-300 mt-1">※ 서버 연결 실패 - 목업 데이터 표시 중</p>}
          </>
        )}
      </div>

      {/* 카테고리 도넛 차트 */}
      <div className="rounded-2xl border border-gray-100 p-4 shadow-sm">
        <p className="text-xs text-gray-500 font-semibold mb-3">🏷️ 카테고리별 소비 내역</p>
        <div className="flex items-center gap-4">
          <PieChart width={120} height={120}>
            <Pie data={MOCK_CATEGORY} cx={55} cy={55} innerRadius={32} outerRadius={55} dataKey="value">
              {MOCK_CATEGORY.map((entry, i) => (
                <Cell key={i} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={(v) => `${v}%`} />
          </PieChart>
          <div className="flex flex-col gap-1.5 flex-1">
            {MOCK_CATEGORY.map((c) => (
              <div key={c.name} className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: c.color }} />
                <span className="text-xs text-gray-600 flex-1">{c.name}</span>
                <span className="text-xs font-semibold text-gray-800">{c.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* TOP 3 바 차트 */}
      <div className="rounded-2xl border border-gray-100 p-4 shadow-sm">
        <div className="flex justify-between items-center mb-3">
          <p className="text-xs text-gray-500 font-semibold">TOP 3 소비 금액</p>
          <button onClick={() => navigate('/report/detail')} className="text-[10px] text-[#1e73be] underline">
            자세히 보기 →
          </button>
        </div>
        <ResponsiveContainer width="100%" height={90}>
          <BarChart data={MOCK_TOP3} layout="vertical" margin={{ left: 8, right: 16 }}>
            <XAxis type="number" hide />
            <YAxis type="category" dataKey="name" width={32} tick={{ fontSize: 11 }} />
            <Bar dataKey="amount" radius={[0, 4, 4, 0]}>
              {MOCK_TOP3.map((_, i) => (
                <Cell key={i} fill={['#1e73be', '#38BDF8', '#60a5fa'][i]} />
              ))}
            </Bar>
            <Tooltip formatter={(v) => `${v.toLocaleString()}원`} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 주별 라인 차트 */}
      <div className="rounded-2xl border border-gray-100 p-4 shadow-sm">
        <p className="text-xs text-gray-500 font-semibold mb-3">📈 주별 소비 변화 추이</p>
        <ResponsiveContainer width="100%" height={100}>
          <LineChart data={MOCK_WEEKLY}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="week" tick={{ fontSize: 10 }} />
            <YAxis hide />
            <Tooltip formatter={(v) => `${v.toLocaleString()}원`} />
            <Line type="monotone" dataKey="식비" stroke="#1e73be" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="쇼핑" stroke="#38BDF8" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 시간대 패턴 - 5개 */}
      <div className="rounded-2xl border border-gray-100 p-4 shadow-sm">
        <p className="text-xs text-gray-500 font-semibold mb-3">⏰ 시간대별 소비 패턴</p>
        <div className="flex justify-between">
          {MOCK_TIME.map((t) => (
            <div key={t.label} className="flex flex-col items-center gap-1">
              <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center text-lg">
                {t.icon}
              </div>
              <p className="text-[10px] font-bold text-gray-700">{t.label}</p>
              <p className="text-[10px] text-[#1e73be] font-semibold">{t.pct}%</p>
            </div>
          ))}
        </div>
        <p className="text-[11px] text-center text-gray-400 mt-3">☀️ 점심 시간대 소비가 가장 활발해요</p>
      </div>

    </div>
  )
}