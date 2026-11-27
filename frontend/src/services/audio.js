// Áudio das chamadas, usando a síntese de voz do próprio navegador.
export function audioDisponivel() {
  return 'speechSynthesis' in window
}

export function falar(texto) {
  if (!audioDisponivel()) return
  window.speechSynthesis.cancel()
  const fala = new SpeechSynthesisUtterance(texto)
  fala.lang = 'pt-BR'
  fala.rate = 0.9
  window.speechSynthesis.speak(fala)
}