'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

interface Representative {
  id: number;
  name: string;
  phone: string;
  email: string;
}

interface Props {
  params: {
    id: string;
  };
}

export default function RepresentativeDetailPage({ params }: Props) {
  const router = useRouter();
  const [rep, setRep] = useState<Representative | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ name: '', phone: '', email: '' });
  const [formError, setFormError] = useState('');

  useEffect(() => {
    fetchRepresentative();
  }, []);

  const fetchRepresentative = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`/api/representatives/${params.id}`);
      setRep(response.data);
      setForm({
        name: response.data.name,
        phone: response.data.phone,
        email: response.data.email,
      });
      setError('');
    } catch (err) {
      setError('خطا در بارگذاری نماینده');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');
    if (!form.name || !form.phone || !form.email) {
      setFormError('لطفا تمام فیلدها را پر کنید');
      return;
    }
    try {
      await axios.put(`/api/representatives/${params.id}`, form);
      router.push('/representatives');
    } catch (err) {
      setFormError('خطا در بروزرسانی نماینده');
    }
  };

  const handleDelete = async () => {
    if (!confirm('آیا از حذف این نماینده مطمئن هستید؟')) {
      return;
    }
    try {
      await axios.delete(`/api/representatives/${params.id}`);
      router.push('/representatives');
    } catch (err) {
      alert('خطا در حذف نماینده');
    }
  };

  if (loading) {
    return <p className="p-6 text-black">در حال بارگذاری...</p>;
  }

  if (error) {
    return <p className="p-6 text-red-600">{error}</p>;
  }

  if (!rep) {
    return <p className="p-6 text-black">نماینده یافت نشد</p>;
  }

  return (
    <main className="p-6 bg-white rounded shadow max-w-md mx-auto" dir="rtl">
      <h1 className="text-2xl font-bold mb-6 text-black">ویرایش نماینده</h1>
      {formError && <p className="text-red-600 mb-4">{formError}</p>}
      <form onSubmit={handleUpdate}>
        <div className="mb-4">
          <label htmlFor="name" className="block mb-1 text-black">نام</label>
          <input
            id="name"
            name="name"
            type="text"
            value={form.name}
            onChange={handleInputChange}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
            required
          />
        </div>
        <div className="mb-4">
          <label htmlFor="phone" className="block mb-1 text-black">تلفن</label>
          <input
            id="phone"
            name="phone"
            type="text"
            value={form.phone}
            onChange={handleInputChange}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
            required
          />
        </div>
        <div className="mb-6">
          <label htmlFor="email" className="block mb-1 text-black">ایمیل</label>
          <input
            id="email"
            name="email"
            type="email"
            value={form.email}
            onChange={handleInputChange}
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
            required
          />
        </div>
        <div className="flex justify-between">
          <button
            type="submit"
            className="bg-black text-white px-4 py-2 rounded hover:bg-gray-800 transition"
          >
            بروزرسانی
          </button>
          <button
            type="button"
            onClick={handleDelete}
            className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition"
          >
            حذف
          </button>
        </div>
      </form>
    </main>
  );
}
