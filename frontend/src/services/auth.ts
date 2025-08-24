import axios from 'axios';
import Cookies from 'js-cookie';

const BASE_URL = 'http://localhost:8080';

interface RegisterData {
  username: string;
  email: string;
  password: string;
  role: string;
}

interface LoginData {
  email: string;
  password: string;
}

export const register = async (data: RegisterData) => {
  const response = await axios.post(`${BASE_URL}/auth/register`, data);
  return response.data;
};

export const login = async (data: LoginData) => {
  const response = await axios.post(`${BASE_URL}/auth/login`, data);
  const { access_token } = response.data;
  Cookies.set('access_token', access_token, { expires: 1 });
  return response.data;
};

export const getRole = async (token: string) => {
  const response = await axios.get(`${BASE_URL}/users/myrole`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const { role } = response.data;
  Cookies.set('role', role, { expires: 1 });
  return role;
};