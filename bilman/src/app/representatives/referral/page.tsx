'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface RepresentativeWithReferrals {
  id: number;
  name: string;
  phone: string;
  email: string;
  referrerId: number | null;
  referrals: RepresentativeWithReferrals[];
}

interface ReferralResponse {
  representative: RepresentativeWithReferrals;
  referralTree: RepresentativeWithReferrals[];
}

export default function ReferralPage() {
  const [data, setData] = useState<ReferralResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [repId, setRepId] = useState('');

  const fetchReferralTree = async () => {
    if (!repId) {
      setError('لطفا شناسه نماینده را وارد کنید');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`/api/representatives/referral?id=${repId}`);
      setData(response.data);
    } catch (err) {
      setError('خطا در بارگذاری درخت ارجاع');
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const renderTree = (nodes: RepresentativeWithReferrals[]) => {
    return (
      <ul className="list-disc list-inside">
        {nodes.map((node) => (
          <li key={node.id} className="text-black">
            {node.name} ({node.phone})
            {node.referrals.length > 0 && renderTree(node.referrals)}
          </li>
        ))}
      </ul>
    );
  };

  return (
    <main className="p-6 bg-white rounded shadow max-w-4xl mx-auto" dir="rtl">
      <h1 className="text-2xl font-bold mb-6 text-black">درخت ارجاع نمایندگان</h1>
      <div className="mb-4 max-w-xs">
        <label htmlFor="repId" className="block mb-1 text-black">شناسه نماینده</label>
        <input
          id="repId"
          type="number"
          value={repId}
          onChange={(e) => setRepId(e.target.value)}
          className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
        />
      </div>
      <button
        onClick={fetchReferralTree}
        className="mb-6 bg-black text-white px-4 py-2 rounded hover:bg-gray-800 transition"
      >
        بارگذاری درخت ارجاع
      </button>
      {loading && <p>در حال بارگذاری...</p>}
      {error && <p className="text-red-600">{error}</p>}
      {data && (
        <div>
          <h2 className="text-xl font-semibold mb-4 text-black">نماینده: {data.representative.name}</h2>
          {renderTree(data.referralTree)}
        </div>
      )}
    </main>
  );
}
