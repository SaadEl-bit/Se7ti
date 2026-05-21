import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm';

const SUPABASE_URL = window.__ENV__?.SUPABASE_URL ?? '';
const SUPABASE_KEY = window.__ENV__?.SUPABASE_KEY ?? '';
const SUPABASE_CONFIGURED = !!(SUPABASE_URL && SUPABASE_KEY);

const supabase = SUPABASE_CONFIGURED ? createClient(SUPABASE_URL, SUPABASE_KEY) : null;

export async function isAuthenticated() {
  if (!supabase) return true;
  const { data } = await supabase.auth.getSession();
  return !!data.session;
}

export async function getCurrentUser() {
  if (!supabase) return null;
  const { data } = await supabase.auth.getUser();
  return data.user;
}

export async function signIn(email, password) {
  if (!supabase) throw new Error('Supabase non configuré — mode démo actif.');
  const { data, error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) throw new Error(error.message);
  return data.user;
}

export async function signUp(email, password, metadata = {}) {
  if (!supabase) throw new Error('Supabase non configuré — mode démo actif.');
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: { data: metadata },
  });
  if (error) throw new Error(error.message);
  return data.user;
}

export async function signOut() {
  if (supabase) await supabase.auth.signOut();
  window.location.href = '/pages/login.html';
}

// ── Login page UI logic ────────────────────────────────────────────────────

const formLogin = document.getElementById('form-login');
const formSignup = document.getElementById('form-signup');
const tabLogin = document.getElementById('tab-login');
const tabSignup = document.getElementById('tab-signup');
const alertContainer = document.getElementById('alert-container');
const btnLogout = document.getElementById('btn-logout');

function showAlert(message, type = 'danger') {
  if (!alertContainer) return;
  alertContainer.innerHTML = `<div class="alert alert--${type}">${message}</div>`;
}

if (tabLogin && tabSignup) {
  tabLogin.addEventListener('click', () => {
    tabLogin.classList.add('active');
    tabSignup.classList.remove('active');
    formLogin.style.display = '';
    formSignup.style.display = 'none';
    alertContainer.innerHTML = '';
  });

  tabSignup.addEventListener('click', () => {
    tabSignup.classList.add('active');
    tabLogin.classList.remove('active');
    formSignup.style.display = '';
    formLogin.style.display = 'none';
    alertContainer.innerHTML = '';
  });
}

if (formLogin) {
  formLogin.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = formLogin.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.textContent = 'Connexion…';
    try {
      await signIn(
        document.getElementById('login-email').value,
        document.getElementById('login-password').value,
      );
      window.location.href = 'map.html';
    } catch (err) {
      showAlert(err.message);
      btn.disabled = false;
      btn.textContent = 'Se connecter';
    }
  });
}

if (formSignup) {
  const btnGeo = document.getElementById('btn-geolocate');
  const geoStatus = document.getElementById('geo-status');

  if (btnGeo) {
    btnGeo.addEventListener('click', () => {
      if (!navigator.geolocation) {
        geoStatus.textContent = 'Géolocalisation non supportée.';
        return;
      }
      geoStatus.textContent = 'Localisation en cours…';
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          document.getElementById('signup-lat').value = pos.coords.latitude.toFixed(6);
          document.getElementById('signup-lon').value = pos.coords.longitude.toFixed(6);
          geoStatus.textContent = 'Position détectée ✓';
        },
        () => {
          geoStatus.textContent = 'Impossible de détecter la position. Entrez manuellement.';
        },
      );
    });
  }

  formSignup.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = formSignup.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.textContent = 'Création…';
    try {
      const pseudo = document.getElementById('signup-pseudo').value.trim();
      const email = document.getElementById('signup-email').value;
      const password = document.getElementById('signup-password').value;
      const phone = document.getElementById('signup-phone')?.value.trim() ?? '';
      const lat = parseFloat(document.getElementById('signup-lat').value);
      const lon = parseFloat(document.getElementById('signup-lon').value);

      await signUp(email, password, { pseudo, phone, latitude: lat, longitude: lon });
      showAlert('Compte créé. Vérifiez votre email pour confirmer.', 'success');
    } catch (err) {
      showAlert(err.message);
    } finally {
      btn.disabled = false;
      btn.textContent = 'Créer un compte';
    }
  });
}

if (btnLogout) {
  btnLogout.addEventListener('click', (e) => { e.preventDefault(); signOut(); });
}
