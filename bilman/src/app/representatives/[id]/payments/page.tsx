'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Payment {
  id: number;
  representativeId: number;
  amount: number;
  date: string;
  note: string;
}

interface Props {
  params: {
    id: string;
  };
}

export default function PaymentHistoryPage({ params }: Props) {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPayments();
  }, []);

  const fetchPayments = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`/api/payments/history?representativeId=${params.id}`);
      setPayments(response.data);
      setError('');
    } catch (err) {
      setError('خطا در بارگذاری تاریخچه پرداخت‌ها');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="p-6 bg-white rounded shadow max-w-md mx-auto" dir="rtl">
      <h1 className="text-2xl font-bold mb-6 text-black">تاریخچه پرداخت‌ها</h1>

      {loading ? (
        <p>در حال بارگذاری...</p>
      ) : error ? (
        <p className="text-red-600">{error}</p>
      ) : payments.length === 0 ? (
        <p>هیچ پرداختی یافت نشد.</p>
      ) : (
        <table className="w-full border border-gray-300">
          <thead>
            <tr className="bg-gray-100 text-black">
              <th className="border border-gray-300 p-2">شناسه</th>
              <th className="border border-gray-300 p-2">مبلغ</th>
              <th className="border border-gray-300 p-2">تاریخ</th>
              <th className="border border-gray-300 p-2">یادداشت</th>
            </tr>
          </thead>
          <tbody>
            {payments.map((payment) => (
              <tr key={payment.id} className="text-black">
                <td className="border border-gray-300 p-2 text-center">{payment.id}</td>
                <td className="border border-gray-300 p-2">{payment.amount.toLocaleString()}</td>
                <td className="border border-gray-300 p-2">{payment.date}</td>
                <td className="border border-gray-300 p-2">{payment.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}
