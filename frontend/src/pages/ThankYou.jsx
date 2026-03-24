import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Galaxy from "./Galaxy";
import "./ThankYou.css";

const CONFETTI_COLORS = ['#00e5ff', '#10b981', '#f59e0b', '#a855f7', '#ec4899'];

export default function ThankYou() {
  const navigate = useNavigate();
  const ran = useRef(false);

  // Read results BEFORE clearing them
  const [finalScore] = useState(() => {
    try {
      const r2 = JSON.parse(localStorage.getItem('round2Result') || '{}');
      const r1 = JSON.parse(localStorage.getItem('round1Result') || '{}');
      const student = JSON.parse(localStorage.getItem('studentEntry') || '{}');
      
      return {
        round1: r1.round1_score ?? r2.round1_score ?? 0,
        round2: r2.round2_score ?? 0,
        total: r2.total_score ?? r1.round1_score ?? 0,
        name: student.name || r2.name || r1.name || "Participant",
      };
    } catch { return null; }
  });

  useEffect(() => {
    window.history.pushState(null, '', window.location.href);
    const blockBack = () => window.history.pushState(null, '', window.location.href);
    window.addEventListener('popstate', blockBack);

    if (ran.current) return;
    ran.current = true;

    // Clear session after a short delay so the UI can render once
    const timer = setTimeout(() => {
      localStorage.removeItem('studentId');
      localStorage.removeItem('studentToken');
      localStorage.removeItem('studentEntry');
      localStorage.removeItem('round1Result');
      localStorage.removeItem('round2Result');
      localStorage.removeItem('currentRound');
      localStorage.removeItem('r2_draft_code');
    }, 1000);

    return () => {
      window.removeEventListener('popstate', blockBack);
      clearTimeout(timer);
    };
  }, []);

  return (
    <div className="ty-page">
      {/* Galaxy Background */}
      <div className="ty-galaxy-bg">
        <Galaxy
          mouseRepulsion
          mouseInteraction
          density={0.8}
          glowIntensity={0.2}
          saturation={0}
          hueShift={140}
          twinkleIntensity={0.3}
          rotationSpeed={0.05}
          repulsionStrength={1.5}
          autoCenterRepulsion={0}
          starSpeed={0.3}
          speed={0.8}
          transparent={false}
        />
      </div>

      <div className="ty-content-wrapper">
        <header className="ty-header">
          <div className="ty-header-content">
            <h1 className="ty-brand">CODEVERSE 2K25</h1>
            <p className="ty-tagline">Competition Successfully Completed</p>
          </div>
        </header>

        <main className="ty-main">
          <div className="ty-hero">
            <div className="ty-trophy">🏆</div>
            <h2 className="ty-title">Congratulations, {finalScore?.name}!</h2>
            <p className="ty-subtitle">You have successfully completed the challenge.</p>

            {/* ── Score Card ── */}
            {finalScore && (
              <div className="ty-score-card">
                <div className="ty-score-header">Final Performance Summary</div>
                <div className="ty-score-rows">
                  <div className="ty-score-row">
                    <span className="ty-score-label">Round 1 (MCQ)</span>
                    <span className="ty-score-value">{finalScore.round1} pts</span>
                  </div>
                  {finalScore.round2 > 0 && (
                    <div className="ty-score-row">
                      <span className="ty-score-label">Round 2 (Debugging)</span>
                      <span className="ty-score-value">{finalScore.round2} pts</span>
                    </div>
                  )}
                  <div className="ty-score-row total">
                    <span className="ty-score-label">Total Aggregate Score</span>
                    <span className="ty-score-value">{finalScore.total} pts</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="ty-announcement">
            <span className="announcement-icon">📢</span>
            <p>Official results and rankings will be announced during the prize ceremony. Keep an eye on your registered email!</p>
          </div>

          <button className="ty-home-btn" onClick={() => navigate('/')}>
            Return to Homepage
          </button>
        </main>

        <footer className="ty-footer">
          <div className="footer-col">
            <h3>JCT College</h3>
            <a href="https://www.jct.ac.in/" target="_blank" rel="noreferrer">www.jct.ac.in</a>
            <p>Phone: +91 9361488801</p>
          </div>
          <div className="footer-col">
            <h3>Connect</h3>
            <div className="social-links">
              <a href="https://www.facebook.com/jctgroups/" target="_blank" rel="noreferrer">Facebook</a>
              <a href="https://www.instagram.com/jct_college/" target="_blank" rel="noreferrer">Instagram</a>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
