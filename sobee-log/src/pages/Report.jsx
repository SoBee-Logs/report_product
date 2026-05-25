import { useState, useEffect, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  PieChart, Pie, Cell, Tooltip,
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer,
  LineChart, Line, CartesianGrid, LabelList
} from 'recharts'

function RecommendCard({ item, index }) {
  const navigate = useNavigate()
  const { product_name, product_company, product_img_url, product_type, content } = item
  const label = product_type === 'card' ? '💳 추천 카드' : '🏦 추천 예적금'

  return (
    <div
      onClick={() => navigate('/product/detail', { state: { item } })}
      className="rounded-2xl border border-gray-100 p-4 shadow-sm flex gap-3 items-center cursor-pointer active:bg-gray-50"
    >
      <div className="shrink-0 w-12 rounded-lg overflow-hidden shadow-md"
        style={{ height: 76, background: 'linear-gradient(135deg, #1e73be, #0e3f78)' }}
      >
        {product_img_url ? (
          <img
            src={product_img_url}
            alt={product_name}
            className="w-full h-full object-cover"
            onError={(e) => { e.currentTarget.style.display = 'none' }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-2xl">
            {product_type === 'card' ? '💳' : '🏦'}
          </div>
        )}
      </div>

      <div className="flex-1 min-w-0">
        <span className="text-[10px] bg-blue-100 text-[#1e73be] rounded-full px-2 py-0.5 font-semibold">{label}</span>
        <p className="text-sm font-bold text-gray-900 mt-1 truncate">{product_name}</p>
        {item.reason && (
          <p className="text-[11px] text-[#1e73be] mt-0.5 leading-snug line-clamp-2">{item.reason}</p>
        )}
      </div>

      <span className="text-gray-300 text-sm shrink-0">›</span>
    </div>
  )
}

const CATEGORY_PALETTE = [
  '#1e73be', '#38BDF8', '#60a5fa', '#93c5fd', '#0ea5e9',
  '#3b82f6', '#7dd3fc', '#2563eb', '#6366f1', '#bfdbfe',
]

const TIME_ICONS = {
  '새벽': '🌙', '아침': '🌅', '점심': '☀️', '저녁': '🍽️', '심야': '🌃',
}
const TIME_ORDER = ['새벽', '아침', '점심', '저녁', '심야']

const API_BASE = 'http://localhost:8000'
const USER_ID = 1

export default function Report() {
  const navigate = useNavigate()
  const location = useLocation()
  const aiRecommendRef = useRef(null)
  const [persona,        setPersona]        = useState(null)
  const [lifecycle,      setLifecycle]      = useState(null)
  const [txData,         setTxData]         = useState(null)
  const [recommendData,  setRecommendData]  = useState(null)
  const [loading,        setLoading]        = useState(true)
  const [error,          setError]          = useState(null)

  useEffect(() => {
    if (location.state?.scrollTo === 'aiRecommend' && aiRecommendRef.current) {
      setTimeout(() => {
        aiRecommendRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 300)
    }
  }, [loading, location.state])

  useEffect(() => {
    const fetchAll = async () => {
      try {
        setLoading(true)
        fetch(`http://localhost:8080/api/users/${USER_ID}/persona`)
          .then(r => r.json())
          .then(setPersona)
          .catch(() => {})

        const [lcRes, txRes] = await Promise.allSettled([
          fetch(`${API_BASE}/api/lifecycle/${USER_ID}`).then(r => r.json()),
          fetch(`${API_BASE}/report/mydata/transaction?user_id=${USER_ID}`).then(r => r.json()),
        ])
        if (lcRes.status === 'fulfilled') setLifecycle(lcRes.value)
        else setLifecycle({ lifecycle_stage: '생애주기 없음', description: '분석 결과를 불러올 수 없어요.' })
        if (txRes.status === 'fulfilled') setTxData(txRes.value)

        try {
          const recRes = await fetch(`${API_BASE}/report/ai-insight?user_id=1`)
          const recData = await recRes.json()
          setRecommendData(recData)
        } catch {
          setRecommendData({ error: true })
        }
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    fetchAll()
  }, [])

  const categoryList = txData
    ? (() => {
        const total = Object.values(txData.category_price).reduce((a, b) => a + b, 0)
        return Object.entries(txData.category_price)
          .sort((a, b) => b[1] - a[1])
          .map(([name, amount], i) => ({
            name,
            amount,
            value: Math.round((amount / total) * 100),
            color: CATEGORY_PALETTE[i % CATEGORY_PALETTE.length],
          }))
      })()
    : []

  const top3 = categoryList.slice(0, 3)

  const timeList = txData
    ? (() => {
        const total = Object.values(txData.timepattern_price).reduce((a, b) => a + b, 0)
        return TIME_ORDER.map(label => ({
          label,
          pct: txData.timepattern_price[label]
            ? Math.round((txData.timepattern_price[label] / total) * 100)
            : 0,
          icon: TIME_ICONS[label],
        }))
      })()
    : []

  const peakTime = timeList.length > 0
    ? timeList.reduce((a, b) => a.pct > b.pct ? a : b)
    : null

  if (loading) return (
    <div className="flex flex-col items-center justify-center h-64 gap-3">
      <span className="animate-spin text-2xl">⏳</span>
      <p className="text-sm text-gray-400">리포트 불러오는 중...</p>
    </div>
  )

  return (
    <div className="flex flex-col gap-4 pt-4 px-4 pb-24 overflow-y-auto">

      {/* 페르소나 배너 */}
      <div className="rounded-2xl bg-[#1e73be] text-white p-4 flex items-center gap-3">
        <div className="w-14 h-14 rounded-full bg-white/20 overflow-hidden shrink-0">
          {persona?.avatarImgUrl
            ? <img src={persona.avatarImgUrl} alt="페르소나" className="w-full h-full object-cover" />
            : <div className="w-full h-full flex items-center justify-center text-2xl">🐝</div>
          }
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs text-blue-100 mb-0.5">나의 소비 페르소나</p>
          <p className="font-bold text-base leading-tight">{persona?.avatarName ?? '분석 중...'}</p>
          <p className="text-xs text-blue-100 mt-0.5 truncate">{persona?.avatarExplane ?? ''}</p>
        </div>
      </div>

      {/* 이번 달 총 소비 */}
      <div className="rounded-2xl border border-gray-100 p-4 shadow-sm">
        <p className="text-xs text-gray-400 mb-1">📊 소비 리포트</p>
        <div className="flex items-end gap-2">
          <span className="text-2xl font-extrabold text-gray-900">
            {txData ? txData.payment_out.toLocaleString() : '-'}원
          </span>
        </div>
        <div className="flex gap-3 mt-3">
          {[
            ['결제 건수', txData ? `${txData.payment_total_num}건` : '-'],
            ['결제 일수', txData ? `${txData.payment_days}일` : '-'],
            ['결제 시간', peakTime ? `${peakTime.icon}${peakTime.label}` : '-'],
          ].map(([label, val]) => (
            <div key={label} className="flex-1 rounded-xl bg-gray-50 p-2 text-center">
              <p className="text-[10px] text-gray-400">{label}</p>
              <p className="text-sm font-bold text-gray-800">{val}</p>
            </div>
          ))}
        </div>
      </div>

      {/* AI 상품 추천 */}
      <div ref={aiRecommendRef} className="flex flex-col gap-2">
        <p className="text-xs text-gray-500 font-semibold">🤖 AI 상품 추천</p>
        {recommendData?.message && (
          <p className="text-[11px] text-gray-400 leading-relaxed px-1">{recommendData.message}</p>
        )}
        {recommendData?.recommned?.length > 0
          ? recommendData.recommned.map((item, i) => (
              <RecommendCard key={i} item={item} index={i} />
            ))
          : recommendData === null
            ? (
              <div className="rounded-2xl border border-gray-100 p-4 shadow-sm text-center text-xs text-gray-400">
                추천 상품을 불러오는 중...
              </div>
            )
            : (
              <div className="rounded-2xl border border-gray-100 p-4 shadow-sm text-center text-xs text-gray-400">
                추천 상품을 불러올 수 없어요
              </div>
            )
        }
      </div>

      {/* 생애주기 */}
      <div className="rounded-2xl border border-blue-100 bg-blue-50 p-4">
        <p className="text-xs text-[#1e73be] font-semibold mb-2">🧬 AI 생애주기 분석</p>
        <p className="font-bold text-[#1e73be] text-base">{lifecycle?.life_stage_code}</p>
        <p className="text-xs text-blue-400 mt-1 leading-relaxed">{lifecycle?.description}</p>
        {error && <p className="text-[10px] text-red-300 mt-1">※ 서버 연결 실패</p>}
      </div>

      {/* 카테고리 도넛 + TOP3 통합 카드 */}
      {categoryList.length > 0 && (
        <div className="rounded-2xl border border-gray-100 p-4 shadow-sm">
          <div className="flex justify-between items-center mb-3">
            <p className="text-xs text-gray-500 font-semibold">🏷️ 카테고리별 소비 내역</p>
            <button
              onClick={() => navigate('/report/detail', { state: { scrollTo: 'category' } })}
              className="text-[10px] text-[#1e73be] underline"
            >
              더보기 →
            </button>
          </div>

          {/* 상단: 도넛 + 비중 % 리스트 */}
          <div className="flex items-center gap-4">
            <PieChart width={120} height={120}>
              <Pie data={categoryList} cx={55} cy={55} innerRadius={32} outerRadius={55} dataKey="value">
                {categoryList.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip formatter={(v) => `${v}%`} />
            </PieChart>
            <div className="flex flex-col gap-1.5 flex-1">
              {categoryList.slice(0, 5).map((c) => (
                <div key={c.name} className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: c.color }} />
                  <span className="text-xs text-gray-600 flex-1">{c.name}</span>
                  <span className="text-xs font-semibold text-gray-800">{c.value}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* 구분선 + 하단: TOP3 막대 (금액) */}
          {top3.length > 0 && (
            <>
              <div className="border-t border-gray-100 my-3" />
              <p className="text-[10px] text-gray-400 mb-2">TOP 3 소비금액</p>
              <ResponsiveContainer width="100%" height={130}>
                <BarChart
                  data={top3}
                  layout="vertical"
                  margin={{ left: 8, right: 80, top: 4, bottom: 4 }}
                >
                  <XAxis type="number" hide />
                  <YAxis type="category" dataKey="name" width={80} tick={{ fontSize: 11 }} interval={0} />
                  <Bar dataKey="amount" radius={[0, 4, 4, 0]}>
                    {top3.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                    <LabelList
                      dataKey="amount"
                      position="right"
                      formatter={(v) => `${v.toLocaleString()}원`}
                      style={{ fontSize: 11, fill: '#374151', fontWeight: 600 }}
                    />
                  </Bar>
                  <Tooltip formatter={(v) => `${v.toLocaleString()}원`} />
                </BarChart>
              </ResponsiveContainer>
            </>
          )}
        </div>
      )}

      {/* 주별 라인 차트 */}
      {txData?.weekly_price?.length > 0 && (
        <div className="rounded-2xl border border-gray-100 p-4 shadow-sm">
          <div className="flex justify-between items-center mb-3">
            <p className="text-xs text-gray-500 font-semibold">📈 주별 소비 변화 추이</p>
            <button
              onClick={() => navigate('/report/detail', { state: { scrollTo: 'weekly' } })}
              className="text-[10px] text-[#1e73be] underline"
            >
              더보기 →
            </button>
          </div>
          <ResponsiveContainer width="100%" height={100}>
            <LineChart data={txData.weekly_price}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="week" tick={{ fontSize: 10 }} />
              <YAxis hide />
              <Tooltip formatter={(v) => `${v.toLocaleString()}원`} />
              {txData.weekly_categories.map((cat, i) => (
                <Line
                  key={cat}
                  type="monotone"
                  dataKey={cat}
                  stroke={CATEGORY_PALETTE[i % CATEGORY_PALETTE.length]}
                  strokeWidth={2}
                  dot={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
          <div className="flex gap-3 mt-2 justify-center flex-wrap">
            {txData.weekly_categories.map((cat, i) => (
              <div key={cat} className="flex items-center gap-1">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ background: CATEGORY_PALETTE[i % CATEGORY_PALETTE.length] }}
                />
                <span className="text-[10px] text-gray-500">{cat}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 시간대 패턴 */}
      {timeList.length > 0 && (
        <div className="rounded-2xl border border-gray-100 p-4 shadow-sm">
          <div className="flex justify-between items-center mb-3">
            <p className="text-xs text-gray-500 font-semibold">⏰ 시간대별 소비 패턴</p>
            <button
              onClick={() => navigate('/report/detail', { state: { scrollTo: 'time' } })}
              className="text-[10px] text-[#1e73be] underline"
            >
              더보기 →
            </button>
          </div>
          <div className="flex justify-between">
            {timeList.map((t) => (
              <div key={t.label} className="flex flex-col items-center gap-1">
                <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center text-lg">{t.icon}</div>
                <p className="text-[10px] font-bold text-gray-700">{t.label}</p>
                <p className="text-[10px] text-[#1e73be] font-semibold">{t.pct}%</p>
              </div>
            ))}
          </div>
          {peakTime && (
            <p className="text-[11px] text-center text-gray-400 mt-3">
              {peakTime.icon} {peakTime.label} 시간대 소비가 가장 활발해요
            </p>
          )}
        </div>
      )}

    </div>
  )
}