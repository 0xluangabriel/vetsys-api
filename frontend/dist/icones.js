export const PATA = '<svg viewBox="0 0 64 64" fill="currentColor" aria-hidden="true"><ellipse cx="13" cy="28" rx="5.5" ry="7.5" transform="rotate(-20 13 28)"/><ellipse cx="24" cy="15" rx="5.5" ry="8"/><ellipse cx="40" cy="15" rx="5.5" ry="8"/><ellipse cx="51" cy="28" rx="5.5" ry="7.5" transform="rotate(20 51 28)"/><path d="M32 30c-9 0-17 9.5-17 17.5 0 6 5 9 10 8 3-.6 4.5-2 7-2s4 1.4 7 2c5 1 10-2 10-8 0-8-8-17.5-17-17.5z"/></svg>';
const traco = (d) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`;
export const ICONES = {
    inicio: traco('<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-5h4v5"/>'),
    tutores: traco('<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>'),
    animais: PATA,
    procedimentos: traco('<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3h6v1M9 11h6M9 15h4"/>'),
    usuarios: traco('<path d="M12 3l7 3v5c0 5-3.5 8.5-7 10-3.5-1.5-7-5-7-10V6z"/><path d="M9 12l2 2 4-4"/>'),
    agenda: traco('<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>'),
    vacina: traco('<path d="M18 2l4 4M15 5l4 4M17 7l-9 9M6 14l4 4M4 20l3-3M11 8l5 5"/>'),
    carteira: traco('<rect x="3" y="6" width="18" height="13" rx="2"/><path d="M3 10h18M7 15h3"/>'),
    busca: traco('<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>'),
    mais: traco('<path d="M12 5v14M5 12h14"/>'),
    sol: traco('<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>'),
    lua: traco('<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>'),
    sair: traco('<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>'),
};
