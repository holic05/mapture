// 숨은 씬 메뉴: ☰ 길게 누르면 열리는 씬 목록 시트

/**
 * @param {HTMLElement} root   #app
 * @param {Array} scenes
 * @param {string} currentId
 * @param {(scene: object) => void} onPick
 */
export function openSceneMenu(root, scenes, currentId, onPick) {
  if (root.querySelector('.sheet-backdrop')) return;

  const backdrop = document.createElement('div');
  backdrop.className = 'sheet-backdrop';
  backdrop.innerHTML = '<div class="sheet"><div class="sheet-grip"></div><p class="sheet-title">Scenes</p><div class="sheet-list"></div></div>';
  const list = backdrop.querySelector('.sheet-list');

  const close = () => backdrop.remove();

  for (const scene of scenes) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'sheet-item' + (scene.id === currentId ? ' current' : '');
    const id = document.createElement('span');
    id.className = 'sid';
    id.textContent = scene.id;
    const title = document.createElement('span');
    title.textContent = scene.title || '';
    const meta = document.createElement('span');
    meta.className = 'meta';
    meta.textContent = `${scene.plan || 'Free'} · ${scene.profile || 'E'}`;
    btn.append(id, title, meta);
    btn.addEventListener('click', () => { close(); onPick(scene); });
    list.appendChild(btn);
  }

  // 길게 누른 손가락을 떼는 순간의 클릭으로 바로 닫히지 않도록 잠깐 뒤부터 배경 탭을 받는다
  const openedAt = performance.now();
  backdrop.addEventListener('click', (e) => {
    if (e.target === backdrop && performance.now() - openedAt > 350) close();
  });

  root.appendChild(backdrop);
  list.querySelector('.current')?.scrollIntoView({ block: 'center' });
}
