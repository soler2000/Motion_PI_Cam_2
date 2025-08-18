// Minimal WHEP client for MediaMTX
export async function playWhep(videoEl, path="/whep/cam") {
  const pc = new RTCPeerConnection({ iceServers: [] });
  pc.addTransceiver("video", { direction: "recvonly" });
  pc.addEventListener("track", (ev) => { videoEl.srcObject = ev.streams[0]; });
  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);

  const resp = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/sdp" },
    body: offer.sdp
  });
  if (!resp.ok) { console.error("WHEP offer failed", resp.status); return; }
  const answerSdp = await resp.text();
  await pc.setRemoteDescription({ type:"answer", sdp:answerSdp });
  return pc;
}
