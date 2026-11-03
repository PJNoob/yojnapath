"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Room } from "livekit-client";

type CallState = "ready" | "connecting" | "active" | "ended" | "error";
type SessionResponse = { livekitUrl: string; participantToken: string; maxDurationSeconds: number };

export function useWebCall() {
  const [state, setState] = useState<CallState>("ready");
  const [message, setMessage] = useState("Ready when you are");
  const [muted, setMuted] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const roomRef = useRef<Room | null>(null);
  const timerRef = useRef<number | null>(null);
  const limitRef = useRef<number | null>(null);

  const stopTimer = useCallback(() => {
    if (timerRef.current !== null) window.clearInterval(timerRef.current);
    timerRef.current = null;
    if (limitRef.current !== null) window.clearTimeout(limitRef.current);
    limitRef.current = null;
  }, []);

  const endCall = useCallback(() => {
    stopTimer();
    roomRef.current?.disconnect();
    roomRef.current = null;
    document.querySelectorAll("audio[data-livekit-web-audio]").forEach((element) => element.remove());
    setState("ended");
    setMessage("Call ended. Thank you for speaking with YojnaPath.");
    setAudioLevel(0);
  }, [stopTimer]);

  const startCall = useCallback(async (accessCode: string) => {
    if (state === "connecting" || state === "active") return;
    if (!accessCode.trim()) {
      setMessage("Enter your access code to start a call.");
      return;
    }
    setState("connecting");
    setMessage("Connecting your call…");
    setSeconds(0);
    setMuted(false);
    try {
      const response = await fetch("/api/web-call/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ accessCode: accessCode.trim() }),
      });
      const body = await response.json() as SessionResponse & { error?: string };
      if (!response.ok) throw new Error(body.error ?? "Could not start the call.");

      const livekit = await import("livekit-client");
      const room = new livekit.Room({ adaptiveStream: true, dynacast: true });
      roomRef.current = room;
      room.on(livekit.RoomEvent.ActiveSpeakersChanged, (speakers) => {
        setAudioLevel(Math.min(1, Math.max(0, ...speakers.map((speaker) => speaker.audioLevel))));
      });
      room.on(livekit.RoomEvent.TrackSubscribed, (track) => {
        if (track.kind !== livekit.Track.Kind.Audio) return;
        const element = track.attach();
        element.autoplay = true;
        element.dataset.livekitWebAudio = "true";
        document.body.append(element);
      });
      room.on(livekit.RoomEvent.Disconnected, () => {
        stopTimer();
        document.querySelectorAll("audio[data-livekit-web-audio]").forEach((element) => element.remove());
        setState("ended");
        setMessage("Call ended. Thank you for speaking with YojnaPath.");
      });
      await room.connect(body.livekitUrl, body.participantToken);
      await room.localParticipant.setMicrophoneEnabled(true);
      setState("active");
      setMessage("Connected");
      timerRef.current = window.setInterval(() => setSeconds((value) => value + 1), 1000);
      limitRef.current = window.setTimeout(endCall, body.maxDurationSeconds * 1000);
    } catch (error) {
      roomRef.current?.disconnect();
      roomRef.current = null;
      setState("error");
      setMessage(error instanceof Error ? error.message : "Could not start the call.");
    }
  }, [endCall, state, stopTimer]);

  const toggleMute = useCallback(async () => {
    if (!roomRef.current || state !== "active") return;
    const nextMuted = !muted;
    await roomRef.current.localParticipant.setMicrophoneEnabled(!nextMuted);
    setMuted(nextMuted);
  }, [muted, state]);

  useEffect(() => () => {
    stopTimer();
    roomRef.current?.disconnect();
    document.querySelectorAll("audio[data-livekit-web-audio]").forEach((element) => element.remove());
  }, [stopTimer]);

  return { state, message, muted, seconds, audioLevel, startCall, toggleMute, endCall };
}
