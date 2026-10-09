import React from 'react'; import { createRoot } from 'react-dom/client'; import App, { Toasts } from './App';
/*
function Login({onLogin}){const [email,setEmail]=useState(''),[password,setPassword]=useState(''),[error,setError]=useState(''); return <main className="auth"><form onSubmit={async e=>{e.preventDefault();try{await api('/auth/login',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({username:email,password})});onLogin()}catch(x){setError(x.message)}}}><h1>Project Hub</h1><p>Đăng nhập để quản lý công việc</p><input type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required/><input type="password" placeholder="Mật khẩu" value={password} onChange={e=>setPassword(e.target.value)} required/><button>Đăng nhập</button>{error&&<small>{error}</small>}</form></main>}
*/
createRoot(document.getElementById('root')).render(<><App /><Toasts /></>);
