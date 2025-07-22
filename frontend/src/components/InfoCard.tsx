import React from 'react';
import { type Point } from '../types';

interface InfoCardProps {
  point: Point;
  setPointRole: (role: 'start' | 'end') => void;
}

const InfoCard: React.FC<InfoCardProps> = ({ point, setPointRole }) => {
  return (
    <div className="info-card">
      <h3>선택된 위치</h3>
      <p><strong>이름:</strong> {point.name}</p>
      <p><strong>좌표:</strong> {point.lat.toFixed(5)}, {point.lon.toFixed(5)}</p>
      <div className="info-card-actions">
        <button onClick={() => setPointRole('start')}>출발지로 설정</button>
        <button onClick={() => setPointRole('end')}>도착지로 설정</button>
      </div>
    </div>
  );
};

export default InfoCard;
