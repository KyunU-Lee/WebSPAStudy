// src/App.jsx 
import { useState, useEffect } from 'react'; 
import axios from 'axios'; 
import { Bar } from 'react-chartjs-2'; 
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

// Chart.js 컴포넌트 등록 
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function App() { const [posts, setPosts] = useState([]); const [loading, setLoading] = useState(true);

useEffect(() => { const fetchPosts = async () => { 
  // ... (기존 API 호출 코드) ... 
  try { const response = await axios.get('https://jsonplaceholder.typicode.com/posts'); setPosts(response.data); setLoading(false); } catch (error) { console.error('API 호출 중 오류 발생:', error); setLoading(false); } };

fetchPosts();
}, []);

// 게시물 데이터를 사용자별로 집계 
const postCountsByUser = posts.reduce((acc, post) => { acc[post.userId] = (acc[post.userId] || 0) + 1; return acc; }, {});

// 차트 데이터 형식에 맞게 변환 
const chartData = { labels: Object.keys(postCountsByUser), datasets: [{ label: '사용자별 게시물 수', data: Object.values(postCountsByUser), backgroundColor: 'rgba(75, 192, 192, 0.6)', }], };

const chartOptions = { responsive: true, plugins: { legend: { position: 'top' }, title: { display: true, text: '사용자별 게시물 수' }, }, };

if (loading) { return
 <h2>로딩 중 ...</h2>
; }
  
return (
  <h2> 완료</h2>
  );
  
}; 
export default App;