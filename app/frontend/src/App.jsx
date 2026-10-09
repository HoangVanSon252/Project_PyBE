import React, { useCallback, useEffect, useState } from 'react';
import './app.css';

const csrf = () => document.cookie.match(/(?:^|; )csrf_token=([^;]+)/)?.[1] || '';
const emitToast = (type, title, message = '') => window.dispatchEvent(new CustomEvent('project-hub-toast', { detail: { type, title, message } }));
export async function api(path, options = {}) {
  const form = options.body instanceof FormData;
  const response = await fetch(path, { credentials: 'include', ...options, headers: { ...(form ? {} : { 'Content-Type': 'application/json' }), 'X-CSRF-Token': csrf(), ...(options.headers || {}) } });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = body.message || ('Request failed (' + response.status + ')');
    emitToast('error', 'Có lỗi xảy ra', message);
    throw new Error(message);
  }
  if (options.method && options.method !== 'GET') emitToast('success', 'Thao tác thành công', body.message || 'Dữ liệu đã được cập nhật.');
  return body.data ?? body;
}
const labels = { TODO: 'Cần làm', IN_PROGRESS: 'Đang làm', DONE: 'Hoàn thành', ADMIN: 'Quản trị viên', MANAGER: 'Quản lý', USER: 'Thành viên', OWNER: 'Chủ dự án', MEMBER: 'Thành viên', VIEWER: 'Chỉ xem' };
function Modal({ title, close, children }) { return <div className="overlay" onMouseDown={close}><div className="modal" onMouseDown={e => e.stopPropagation()}><button className="x" onClick={close}>×</button><h2>{title}</h2>{children}</div></div>; }
function Alert({ value, clear }) { return value ? <div className="alert">{value}<button onClick={clear}>×</button></div> : null; }

export function Toasts() {
  const [items, setItems] = useState([]);
  useEffect(() => {
    const handler = event => {
      const item = { id: Date.now() + Math.random(), ...event.detail };
      setItems(current => [...current, item]);
      window.setTimeout(() => setItems(current => current.filter(value => value.id !== item.id)), 4500);
    };
    window.addEventListener('project-hub-toast', handler);
    return () => window.removeEventListener('project-hub-toast', handler);
  }, []);
  const icons = { success: '✓', info: 'i', warning: '!', error: '×' };
  return <div className="toast-stack" aria-live="polite">{items.map(item => <article className={'toast ' + item.type} key={item.id}><span className="toast-icon">{icons[item.type]}</span><div><b>{item.title}</b><p>{item.message}</p></div><button onClick={() => setItems(current => current.filter(value => value.id !== item.id))}>×</button></article>)}</div>;
}
function Profile({ user, close }) {
  return <Modal title="Tài khoản của tôi" close={close}><section className="profile-card"><div className="profile-avatar">{user.full_name?.slice(0, 1).toUpperCase()}</div><h3>{user.full_name}</h3><p>{user.email}</p><dl><div><dt>Vai trò hệ thống</dt><dd>{labels[user.role]}</dd></div><div><dt>Trạng thái</dt><dd className={user.is_active ? 'ok' : 'bad'}>{user.is_active ? 'Đang hoạt động' : 'Đã khóa'}</dd></div><div><dt>Ngày tạo</dt><dd>{user.created_at ? new Date(user.created_at).toLocaleDateString('vi-VN') : '—'}</dd></div><div><dt>Thời gian sử dụng</dt><dd>{user.account_age_days ?? 0} ngày</dd></div></dl><button className="secondary" onClick={close}>Đóng</button></section></Modal>;
}
function Login({ done }) {
  const [email, setEmail] = useState('admin@example.com'), [password, setPassword] = useState('ChangeMe123!'), [error, setError] = useState('');
  async function submit(e) { e.preventDefault(); const invalid = !/^\S+@\S+\.\S+$/.test(email) ? 'Email không đúng định dạng.' : password.length < 8 ? 'Mật khẩu phải có ít nhất 8 ký tự.' : ''; if (invalid) { setError(invalid); emitToast('warning', 'Kiểm tra lại thông tin', invalid); return; } try { await api('/auth/login', { method: 'POST', body: new URLSearchParams({ username: email, password }), headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }); done(); } catch (err) { setError(err.message); } }
  return <main className="login"><form onSubmit={submit}><b className="logo">PH</b><p className="eyebrow">PROJECT HUB</p><h1>Chào mừng trở lại</h1><p>Đăng nhập để quản lý dự án.</p><label>Email<input value={email} onChange={e => setEmail(e.target.value)} type="email" required /></label><label>Mật khẩu<input value={password} onChange={e => setPassword(e.target.value)} type="password" required /></label><Alert value={error} clear={() => setError('')} /><button className="primary">Đăng nhập</button></form></main>;
}
function ProjectForm({ project, save }) {
  const [name, setName] = useState(project?.name || ''), [description, setDescription] = useState(project?.description || '');
  return <form className="form" onSubmit={e => { e.preventDefault(); const clean = name.trim(); const invalid = clean.length < 5 ? 'Tên dự án cần tối thiểu 5 ký tự.' : clean.length > 50 ? 'Tên dự án tối đa 50 ký tự.' : description.length > 1000 ? 'Mô tả tối đa 1000 ký tự.' : ''; if (invalid) { emitToast('warning', 'Dữ liệu chưa hợp lệ', invalid); return; } save({ name: clean, description: description.trim() }); }}><label>Tên dự án<input minLength="5" maxLength="50" value={name} onChange={e => setName(e.target.value)} required /><small>{name.length}/50</small></label><label>Mô tả<textarea maxLength="1000" value={description} onChange={e => setDescription(e.target.value)} /><small>{description.length}/1000</small></label><button className="primary">Lưu dự án</button></form>;
}
function TaskForm({ task, members, save }) {
  const [data, setData] = useState({ title: task?.title || '', description: task?.description || '', status: task?.status || 'TODO', priority: task?.priority || 'MEDIUM', assignee_id: task?.assignee_id || '' });
  const change = (key, value) => setData(v => ({ ...v, [key]: value }));
  return <form className="form" onSubmit={e => { e.preventDefault(); const title = data.title.trim(), description = data.description.trim(); const invalid = !title ? 'Tiêu đề công việc không được để trống.' : title.length > 255 ? 'Tiêu đề tối đa 255 ký tự.' : description.length > 1000 ? 'Mô tả tối đa 1000 ký tự.' : ''; if (invalid) { emitToast('warning', 'Dữ liệu chưa hợp lệ', invalid); return; } save({ ...data, title, description, assignee_id: data.assignee_id ? Number(data.assignee_id) : null }); }}><label>Tiêu đề<input maxLength="255" value={data.title} onChange={e => change('title', e.target.value)} required /><small>{data.title.length}/255</small></label><label>Mô tả<textarea maxLength="1000" value={data.description} onChange={e => change('description', e.target.value)} /><small>{data.description.length}/1000</small></label><div className="two"><label>Trạng thái<select value={data.status} onChange={e => change('status', e.target.value)}>{['TODO', 'IN_PROGRESS', 'DONE'].map(v => <option key={v}>{v}</option>)}</select></label><label>Ưu tiên<select value={data.priority} onChange={e => change('priority', e.target.value)}>{['LOW', 'MEDIUM', 'HIGH'].map(v => <option key={v}>{v}</option>)}</select></label></div><label>Giao cho<select value={data.assignee_id} onChange={e => change('assignee_id', e.target.value)}><option value="">Chưa giao</option>{members.map(m => <option key={m.user_id} value={m.user_id}>User #{m.user_id} · {labels[m.role]}</option>)}</select></label><button className="primary">Lưu công việc</button></form>;
}
function TaskDetail({ id, close }) {
  const [task, setTask] = useState(null), [comment, setComment] = useState(''), [file, setFile] = useState(null), [error, setError] = useState('');
  const load = useCallback(() => api('/tasks/' + id).then(setTask).catch(e => setError(e.message)), [id]); useEffect(() => { load(); }, [load]);
  if (!task) return <Modal title="Công việc" close={close}><p>{error || 'Đang tải...'}</p></Modal>;
  async function send(e) { e.preventDefault(); const content = comment.trim(); if (!content || content.length > 5000) { emitToast('warning', 'Bình luận chưa hợp lệ', 'Bình luận cần có từ 1 đến 5000 ký tự.'); return; } try { await api('/tasks/' + id + '/comments', { method: 'POST', body: JSON.stringify({ content }) }); setComment(''); load(); } catch (err) { setError(err.message); } }
  async function upload(e) { e.preventDefault(); const allowed = ['jpg', 'jpeg', 'png', 'pdf', 'docx']; const ext = file?.name.split('.').pop()?.toLowerCase(); if (!file || !allowed.includes(ext) || file.size > 5 * 1024 * 1024) { emitToast('warning', 'Tệp chưa hợp lệ', 'Chỉ nhận JPG, PNG, PDF, DOCX và tối đa 5MB.'); return; } const data = new FormData(); data.append('file', file); try { await api('/tasks/' + id + '/attachments', { method: 'POST', body: data }); setFile(null); load(); } catch (err) { setError(err.message); } }
  return <Modal title={task.title} close={close}><Alert value={error} clear={() => setError('')} /><span className={'tag ' + task.status}>{labels[task.status]}</span><span className={'tag priority ' + task.priority}>{task.priority}</span><p className="description">{task.description || 'Không có mô tả.'}</p><small>Người tạo #{task.creator_id} · Phụ trách {task.assignee_id ? '#' + task.assignee_id : 'Chưa giao'}</small><h3>Bình luận</h3>{task.comments.map(c => <article className="comment" key={c.id}><b>User #{c.user_id}</b><p>{c.content}</p></article>)}<form className="inline" onSubmit={send}><input placeholder="Viết bình luận" value={comment} onChange={e => setComment(e.target.value)} required /><button>Gửi</button></form><h3>Tệp đính kèm</h3>{task.attachments.map(a => <p key={a.id}>📎 {a.file_name}</p>)}<form className="inline" onSubmit={upload}><input type="file" accept=".jpg,.jpeg,.png,.pdf,.docx" onChange={e => setFile(e.target.files[0])} /><button>Tải lên</button></form></Modal>;
}
function Workspace({ project, user, back, refresh, removeProject }) {
  const [tasks, setTasks] = useState([]), [members, setMembers] = useState(project.members || []), [task, setTask] = useState(null), [detail, setDetail] = useState(null), [error, setError] = useState(''), [filter, setFilter] = useState('ALL'), [memberId, setMemberId] = useState('');
  const isOwner = project.owner_id === user.id; const own = members.find(m => m.user_id === user.id); const editable = isOwner || own?.role === 'MEMBER';
  const load = useCallback(async () => { try { const result = await api('/projects/' + project.id + '/tasks?size=100'); setTasks(result.items || []); setMembers(await api('/projects/' + project.id + '/members')); } catch (e) { setError(e.message); } }, [project.id]); useEffect(() => { load(); }, [load]);
  async function save(data) { try { if (task?.id) await api('/tasks/' + task.id, { method: 'PATCH', body: JSON.stringify(data) }); else await api('/projects/' + project.id + '/tasks', { method: 'POST', body: JSON.stringify(data) }); setTask(null); load(); refresh(); } catch (e) { setError(e.message); } }
  async function addMember(e) { e.preventDefault(); const id = Number(memberId); if (!Number.isInteger(id) || id < 1) { emitToast('warning', 'User ID chưa hợp lệ', 'Vui lòng nhập User ID là số nguyên dương.'); return; } try { await api('/projects/' + project.id + '/members', { method: 'POST', body: JSON.stringify({ user_id: id, role: 'MEMBER' }) }); setMemberId(''); load(); } catch (e) { setError(e.message); } }
  async function erase(id) { if (!confirm('Xóa công việc này?')) return; try { await api('/tasks/' + id, { method: 'DELETE' }); load(); } catch (e) { setError(e.message); } }
  const visible = filter === 'ALL' ? tasks : tasks.filter(t => t.status === filter);
  return <main className="workspace"><button className="back" onClick={back}>← Tất cả dự án</button><div className="head"><div><p className="eyebrow">DỰ ÁN</p><h1>{project.name}</h1><p>{project.description}</p></div><div>{isOwner && <button className="danger" onClick={() => removeProject(project)}>Xóa dự án</button>}{editable && <button className="primary" onClick={() => setTask({})}>+ Công việc</button>}</div></div><Alert value={error} clear={() => setError('')} /><div className="workspace-grid"><aside><h3>Thành viên ({members.length})</h3>{members.map(m => <p className="member" key={m.user_id}><b>#{m.user_id}</b><span>{labels[m.role]}</span></p>)}{isOwner && <form className="inline" onSubmit={addMember}><input type="number" value={memberId} onChange={e => setMemberId(e.target.value)} placeholder="User ID" required /><button>Thêm</button></form>}</aside><section><div className="tabs">{['ALL', 'TODO', 'IN_PROGRESS', 'DONE'].map(s => <button className={filter === s ? 'active' : ''} key={s} onClick={() => setFilter(s)}>{s === 'ALL' ? 'Tất cả' : labels[s]}</button>)}</div><div className="tasks">{visible.map(t => <article className="task" onClick={() => setDetail(t.id)} key={t.id}><span className={'tag ' + t.status}>{labels[t.status]}</span><span className={'tag priority ' + t.priority}>{t.priority}</span><h3>{t.title}</h3><p>{t.description || 'Không có mô tả'}</p><small>Phụ trách: {t.assignee_id ? '#' + t.assignee_id : '—'}</small>{editable && <div className="task-actions"><button onClick={e => { e.stopPropagation(); setTask(t); }}>Sửa</button><button onClick={e => { e.stopPropagation(); erase(t.id); }}>Xóa</button></div>}</article>)}</div></section></div>{task && <Modal title={task.id ? 'Cập nhật công việc' : 'Tạo công việc'} close={() => setTask(null)}><TaskForm task={task.id ? task : null} members={members} save={save} /></Modal>}{detail && <TaskDetail id={detail} close={() => setDetail(null)} />}</main>;
}
function App() {
  const [user, setUser] = useState(null), [projects, setProjects] = useState([]), [selected, setSelected] = useState(null), [modal, setModal] = useState(false), [tab, setTab] = useState('projects'), [users, setUsers] = useState([]), [error, setError] = useState(''), [profile, setProfile] = useState(false);
  const load = useCallback(async () => { try { setProjects(await api('/projects/')); } catch (e) { setError(e.message); } }, []);
  const boot = useCallback(async () => { try { setUser(await api('/users/me')); await load(); } catch {} }, [load]); useEffect(() => { boot(); }, [boot]);
  useEffect(() => { if (tab === 'users' && user?.role === 'ADMIN') api('/users').then(setUsers).catch(e => setError(e.message)); }, [tab, user]);
  async function saveProject(data) { try { const p = await api('/projects/', { method: 'POST', body: JSON.stringify(data) }); setModal(false); await load(); setSelected(p); } catch (e) { setError(e.message); } }
  async function deleteProject(p) { if (!confirm('Xóa dự án ' + p.name + '?')) return; try { await api('/projects/' + p.id, { method: 'DELETE' }); setSelected(null); load(); } catch (e) { setError(e.message); } }
  if (!user) return <Login done={boot} />;
  if (selected) return <Workspace project={selected} user={user} back={() => setSelected(null)} refresh={load} removeProject={deleteProject} />;
  return <div><header><b>PH <span>Project Hub</span></b><nav><button onClick={() => setTab('projects')}>Dự án</button>{user.role === 'ADMIN' && <button onClick={() => setTab('users')}>Tài khoản</button>}<button className="account-button" onClick={() => setProfile(true)}>{user.full_name} · {labels[user.role]}</button></nav></header><main className="dashboard"><div className="head"><div><p className="eyebrow">KHÔNG GIAN LÀM VIỆC</p><h1>{tab === 'projects' ? 'Dự án của bạn' : 'Tài khoản hệ thống'}</h1></div>{tab === 'projects' && <button className="primary" onClick={() => setModal(true)}>+ Tạo dự án</button>}</div><Alert value={error} clear={() => setError('')} />{tab === 'users' ? <table><thead><tr><th>ID</th><th>Họ tên</th><th>Email</th><th>Vai trò</th><th>Trạng thái</th></tr></thead><tbody>{users.map(u => <tr key={u.id}><td>#{u.id}</td><td>{u.full_name}</td><td>{u.email}</td><td>{labels[u.role]}</td><td>{u.is_active ? 'Hoạt động' : 'Đã khóa'}</td></tr>)}</tbody></table> : <div className="projects">{projects.map(p => <article className="project" onClick={() => setSelected(p)} key={p.id}><b className="project-icon">{p.name[0]}</b><span>{p.owner_id === user.id ? 'OWNER' : 'MEMBER'}</span><h2>{p.name}</h2><p>{p.description || 'Chưa có mô tả'}</p><footer>{p.members?.length || 0} thành viên <b>→</b></footer></article>)}</div>}{modal && <Modal title="Tạo dự án" close={() => setModal(false)}><ProjectForm save={saveProject} /></Modal>}{profile && <Profile user={user} close={() => setProfile(false)} />}</main></div>;
}
export default App;
