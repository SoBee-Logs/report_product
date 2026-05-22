import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import StatusBar from '../components/common/StatusBar'
import { roomFeedPreviews } from '../data/mockDiaries'

const API_BASE = 'http://localhost:8080'
const USER_ID = 1

export default function Home() {
  const navigate = useNavigate()
  const [persona, setPersona] = useState(null)

  useEffect(() => {
    fetch(`${API_BASE}/api/users/${USER_ID}/persona`)
      .then(r => r.json())
      .then(setPersona)
      .catch(() => {})
  }, [])

  return (
    <main className="min-h-full bg-white text-left pb-2">
      <section className="bg-white pb-5">
        <StatusBar />
        <header className="px-5 pt-1 flex items-center gap-2">
          <button
            type="button"
            onClick={() => navigate('/search')}
            className="flex-1 flex items-center gap-2 bg-gray-100 rounded-2xl px-4 py-2.5 text-left"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <span className="text-[13px] text-gray-400">궁금한 걸 자유롭게 물어보세요!</span>
          </button>
          <button type="button" className="text-gray-500 p-1 shrink-0">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
          </button>
        </header>

        <figure className="relative w-full mt-3 mb-0 m-0">
          <img
            src={persona?.avatarImgUrl ?? '/persona-bee.png'}
            alt="페르소나 꿀벌 아바타"
            className="w-full h-auto block"
          />
          <div className="absolute top-3 left-3 bg-black/30 backdrop-blur-sm px-3 py-2 rounded-2xl text-white flex flex-col items-center gap-0">
            <span className="text-[10px] font-light leading-none">나의 소비 페르소나</span>
            <span className="text-[13px] font-extrabold leading-none mt-0.5">{persona?.avatarName ?? '분석 중...'}</span>
          </div>
        </figure>

        <button
          type="button"
          onClick={() => navigate('/report', { state: { scrollTo: 'aiRecommend' } })}
          className="mt-4 mx-5 w-[calc(100%-40px)] py-3.5 rounded-xl bg-[#1e73be] text-white text-[13px] font-bold shadow-md"
        >
          페르소나 기반 금융 상품 추천 바로가기
        </button>
      </section>

      <section className="px-5 -mt-2">
        <button
          type="button"
          onClick={() => navigate('/camera')}
          className="w-full bg-white rounded-3xl px-5 py-5 shadow-md flex items-center gap-4 text-left"
        >
          <span className="flex-1 block">
            <span className="block text-[11px] text-gray-400 mb-1">sytem time</span>
            <span className="block text-[15px] font-bold text-gray-900 leading-snug">
              소비가 있다면
              <br />
              찍어주세요!
            </span>
          </span>
          <span className="w-[68px] h-[68px] border border-gray-200 rounded-2xl flex items-center justify-center bg-white shrink-0">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="1.5">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
              <circle cx="12" cy="13" r="4" />
            </svg>
          </span>
        </button>
      </section>

      <section className="px-5 pt-6 pb-24">
        <h3 className="text-[15px] font-extrabold text-gray-900 mb-1">피드</h3>
        <ul className="grid grid-cols-2 gap-x-4 gap-y-4 list-none p-0 m-0">
          {roomFeedPreviews.map((item) => (
            <li key={item.roomId}>
              <button
                type="button"
                onClick={() => navigate('/feed', { state: { roomId: item.roomId } })}
                className="w-full text-left p-0 border-0 bg-transparent"
              >
                <figure className="relative aspect-square rounded-xl overflow-hidden bg-gray-100 m-0 mb-2">
                  <img src={item.imageUrl} alt="" className="w-full h-full object-cover" />
                  <span className="absolute bottom-2 right-2 text-gray-300">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
                    </svg>
                  </span>
                </figure>
                <p className="text-[13px] font-bold text-gray-900 m-0">{item.roomName}</p>
              </button>
            </li>
          ))}
        </ul>
      </section>
    </main>
  )
}
