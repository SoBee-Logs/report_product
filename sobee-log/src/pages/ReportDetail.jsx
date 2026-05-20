import { useNavigate } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer,
  Tooltip, Legend
} from 'recharts'

const WEEKLY_DETAIL = [
  { week: '1주', 식비: 4200, 쇼핑: 1800, 교통: 3100, 카페: 2100, 생활: 1500, 문화: 800,  금융: 500, 뷰티: 300, 의료: 200,  여행: 0,    술: 1200, 온라인: 900,  주거: 400, 교육: 600, 경조: 0 },
  { week: '2주', 식비: 5100, 쇼핑: 3200, 교통: 2800, 카페: 1900, 생활: 1200, 문화: 1100, 금융: 500, 뷰티: 700, 의료: 0,    여행: 0,    술: 800,  온라인: 1300, 주거: 400, 교육: 600, 경조: 2000 },
  { week: '3주', 식비: 3800, 쇼핑: 2100, 교통: 3500, 카페: 2400, 생활: 900,  문화: 600,  금융: 500, 뷰티: 0,   의료: 1500, 여행: 0,    술: 1500, 온라인: 600,  주거: 400, 교육: 600, 경조: 0 },
  { week: '4주', 식비: 6400, 쇼핑: 3300, 교통: 3400, 카페: 1800, 생활: 2100, 문화: 400,  금융: 500, 뷰티: 500, 의료: 0,    여행: 8000, 술: 2100, 온라인: 2200, 주거: 400, 교육: 600, 경조: 0 },
]

const CATEGORIES = [
  { name: '식비',     key: '식비',   color: '#1e73be', total: 19500 },
  { name: '패션/쇼핑', key: '쇼핑',   color: '#38BDF8', total: 10400 },
  { name: '교통',     key: '교통',   color: '#60a5fa', total: 12800 },
  { name: '카페/간식', key: '카페',   color: '#93c5fd', total:  8200 },
  { name: '생활',     key: '생활',   color: '#2563eb', total:  5700 },
  { name: '문화/여가', key: '문화',   color: '#0ea5e9', total:  2900 },
  { name: '금융',     key: '금융',   color: '#7dd3fc', total:  2000 },
  { name: '뷰티/미용', key: '뷰티',   color: '#bae6fd', total:  1500 },
  { name: '의료/건강', key: '의료',   color: '#1d4ed8', total:  1700 },
  { name: '여행/숙박', key: '여행',   color: '#3b82f6', total:  8000 },
  { name: '술/유흥',  key: '술',    color: '#6366f1', total:  5600 },
  { name: '온라인쇼핑', key: '온라인', color: '#a5b4fc', total:  5000 },
  { name: '주거/통신', key: '주거',   color: '#c7d2fe', total:  1600 },
  { name: '교육/학습', key: '교육',   color: '#dbeafe', total:  2400 },
  { name: '경조/선물', key: '경조',   color: '#bfdbfe', total:  2000 },
]

// 이번주 = 4주차 데이터
const THIS_WEEK = WEEKLY_DETAIL[3]
const MAX_TOTAL = Math.max(...CATEGORIES.map((c) => c.total))
const MAX_WEEK  = Math.max(...CATEGORIES.map((c) => THIS_WEEK[c.key]))

export default function ReportDetail() {
  const navigate = useNavigate()

  return (
    <div className="flex flex-col gap-4 pt-4 px-4 pb-24 overflow-y-auto">

      {/* 카테고리별 월 누적 총합 */}
      <div className="rounded-2xl border border-gray-100 p-4 shadow-sm">
        <p className="text-xs text-gray-500 font-semibold mb-4">📊 이번 달 카테고리별 소비</p>
        <div className="flex flex-col gap-3">
          {CATEGORIES.map((cat) => (
            <div key={cat.name}>
              <div className="flex justify-between items-center mb-1">
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full shrink-0" style={{ background: cat.color }} />
                  <span className="text-xs font-semibold text-gray-700">{cat.name}</span>
                </div>
                <span className="text-xs text-gray-500">{cat.total.toLocaleString()}원</span>
              </div>
              <div className="w-full h-2 rounded-full bg-gray-100">
                <div
                  className="h-2 rounded-full transition-all duration-500"
                  style={{
                    width: `${(cat.total / MAX_TOTAL) * 100}%`,
                    background: cat.color,
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 이번주 소비 - 카테고리별 1개 바 */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <p className="text-xs text-gray-500 font-semibold">📅 이번주 소비</p>
          <span className="text-[10px] text-[#1e73be] bg-blue-50 px-2 py-0.5 rounded-full font-semibold">4주차</span>
        </div>

        {CATEGORIES.map((cat) => (
          <div key={cat.name} className="rounded-2xl border border-gray-100 p-4 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full shrink-0" style={{ background: cat.color }} />
                <p className="text-xs font-semibold text-gray-700">{cat.name}</p>
              </div>
              <div className="text-right">
                <span className="text-sm font-bold" style={{ color: cat.color }}>
                  {THIS_WEEK[cat.key].toLocaleString()}원
                </span>
                <span className="text-[10px] text-gray-400 ml-1">/ 월 {cat.total.toLocaleString()}원</span>
              </div>
            </div>
            <div className="w-full h-2.5 rounded-full bg-gray-100">
              <div
                className="h-2.5 rounded-full transition-all duration-500"
                style={{
                  width: THIS_WEEK[cat.key] === 0 ? '2%' : `${(THIS_WEEK[cat.key] / MAX_WEEK) * 100}%`,
                  background: THIS_WEEK[cat.key] === 0 ? '#e5e7eb' : cat.color,
                }}
              />
            </div>
            {THIS_WEEK[cat.key] === 0 && (
              <p className="text-[10px] text-gray-300 mt-1">이번주 소비 없음</p>
            )}
          </div>
        ))}
      </div>

      {/* 뒤로가기 */}
      <button
        onClick={() => navigate('/report')}
        className="w-full py-3 rounded-2xl bg-[#1e73be] text-white text-sm font-semibold"
      >
        ← 리포트로 돌아가기
      </button>

    </div>
  )
}