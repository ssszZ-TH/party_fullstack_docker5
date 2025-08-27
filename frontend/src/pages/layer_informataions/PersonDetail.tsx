import React, { useState, useEffect, useContext } from 'react';
import { Box, Container, Typography, Paper, Stack, TextField } from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import Cookies from 'js-cookie';
import { getPersonById, updatePerson, createPerson, deletePerson } from '../../services/persons';
import { useTheme } from '../../contexts/ThemeContext';
import { AuthContext } from '../../contexts/AuthContext';
import AppBarCustom from '../../components/AppBarCustom';
import SaveButton from '../../components/buttons/SaveButton';
import CancelButton from '../../components/buttons/CancelButton';
import DeleteButton from '../../components/buttons/DeleteButton';
import Loading from '../../components/Loading';

interface Person {
  id?: number;
  username: string;
  email: string;
  personal_id_number: string;
  first_name: string;
  last_name: string;
  birth_date: string;
  height: number;
  weight: number;
  middle_name?: string | null;
  nick_name?: string | null;
  gender_type_id?: number | null;
  marital_status_type_id?: number | null;
  country_id?: number | null;
  racial_type_id?: number | null;
  income_range_id?: number | null;
  about_me?: string | null;
  created_at?: string;
  updated_at?: string | null;
}

export default function PersonDetail() {
  const { isDarkMode } = useTheme();
  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const { param } = useParams<{ param: string }>();
  const isCreateMode = param === 'create';
  const [person, setPerson] = useState<Person | null>(isCreateMode ? { 
    username: '', 
    email: '', 
    personal_id_number: '', 
    first_name: '', 
    last_name: '', 
    birth_date: '', 
    height: 0, 
    weight: 0 
  } : null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    personal_id_number: '',
    first_name: '',
    last_name: '',
    birth_date: '',
    height: '',
    weight: '',
  });
  const [loading, setLoading] = useState(!isCreateMode);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPerson = async () => {
      if (isCreateMode) {
        setLoading(false);
        return;
      }
      try {
        const token = Cookies.get('access_token');
        if (!token) {
          setError('กรุณาเข้าสู่ระบบหรือ token หมดอายุ');
          logout();
          navigate('/login');
          return;
        }
        if (param && !isNaN(Number(param))) {
          const data = await getPersonById(parseInt(param));
          if (data && typeof data === 'object' && 'id' in data) {
            setPerson(data);
            setFormData({
              username: data.username || '',
              email: data.email || '',
              password: '',
              personal_id_number: data.personal_id_number || '',
              first_name: data.first_name || '',
              last_name: data.last_name || '',
              birth_date: data.birth_date || '',
              height: data.height ? data.height.toString() : '',
              weight: data.weight ? data.weight.toString() : '',
            });
          } else {
            setError('Invalid person data');
          }
        } else {
          setError('Invalid person ID');
        }
      } catch (error) {
        console.error('Error fetching person:', error);
        setError('Failed to load person');
        navigate('/persons');
      } finally {
        setLoading(false);
      }
    };
    fetchPerson();
  }, [param, navigate, isCreateMode, logout]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    try {
      const updateData: {
        username?: string;
        email?: string;
        password?: string;
        personal_id_number?: string;
        first_name?: string;
        last_name?: string;
        birth_date?: string;
        height?: number;
        weight?: number;
      } = {};
      if (formData.username) updateData.username = formData.username;
      if (formData.email) updateData.email = formData.email;
      if (formData.password) updateData.password = formData.password;
      if (formData.personal_id_number) updateData.personal_id_number = formData.personal_id_number;
      if (formData.first_name) updateData.first_name = formData.first_name;
      if (formData.last_name) updateData.last_name = formData.last_name;
      if (formData.birth_date) updateData.birth_date = formData.birth_date;
      if (formData.height) updateData.height = parseFloat(formData.height);
      if (formData.weight) updateData.weight = parseFloat(formData.weight);

      if (Object.keys(updateData).length === 0) {
        setError('No changes to save');
        return;
      }

      if (isCreateMode) {
        if (!formData.username || !formData.email || !formData.password || 
            !formData.personal_id_number || !formData.first_name || 
            !formData.last_name || !formData.birth_date || !formData.height || !formData.weight) {
          setError('All required fields must be filled for creating a new person');
          return;
        }
        await createPerson({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          personal_id_number: formData.personal_id_number,
          first_name: formData.first_name,
          last_name: formData.last_name,
          birth_date: formData.birth_date,
          height: parseFloat(formData.height),
          weight: parseFloat(formData.weight),
        });
      } else if (param && !isNaN(Number(param))) {
        if (Object.keys(updateData).length === 1 && updateData.email) {
          setError('Cannot update email only');
          return;
        }
        await updatePerson(parseInt(param), updateData);
      }
      navigate('/persons');
    } catch (error) {
      console.error('Error processing person:', error);
      setError(isCreateMode ? 'Failed to create person' : 'Failed to update person');
    }
  };

  const handleCancel = () => {
    navigate('/persons');
  };

  const handleDelete = async () => {
    if (!param || isNaN(Number(param))) return;
    try {
      await deletePerson(parseInt(param));
      navigate('/persons');
    } catch (error) {
      console.error('Error deleting person:', error);
      setError('Failed to delete person');
    }
  };

  if (loading) {
    return <Loading />;
  }

  if (!isCreateMode && (error || !person)) {
    return (
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography color="error.main">{error || 'No person data available'}</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBarCustom title={isCreateMode ? "Create Person" : "Person Detail"} />
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Paper elevation={3} sx={{ p: 4, borderRadius: 'shape.borderRadius', bgcolor: 'background.paper' }}>
          <Typography variant="h4" sx={{ color: 'text.primary', mb: 2 }}>
            {isCreateMode ? 'Create New Person' : 'Edit Person'}
          </Typography>
          <Box sx={{ mb: 4 }}>
            {!isCreateMode && (
              <TextField
                label="ID"
                value={person?.id || ''}
                fullWidth
                margin="normal"
                variant="outlined"
                disabled
                InputLabelProps={{ style: { color: 'text.secondary' } }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    '&.Mui-disabled fieldset': {
                      borderColor: 'divider',
                    },
                  },
                }}
              />
            )}
            <TextField
              label="Username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              fullWidth
              margin="normal"
              variant="outlined"
              InputLabelProps={{ style: { color: 'text.secondary' } }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  '&.Mui-focused fieldset': {
                    borderColor: 'primary.main',
                  },
                },
              }}
            />
            <TextField
              label="Email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              fullWidth
              margin="normal"
              variant="outlined"
              disabled={!isCreateMode}
              InputLabelProps={{ style: { color: 'text.secondary' } }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  '&.Mui-disabled fieldset': {
                    borderColor: 'divider',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: 'primary.main',
                  },
                },
              }}
            />
            <TextField
              label="Password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              fullWidth
              margin="normal"
              variant="outlined"
              InputLabelProps={{ style: { color: 'text.secondary' } }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  '&.Mui-focused fieldset': {
                    borderColor: 'primary.main',
                  },
                },
              }}
            />
            <TextField
              label="Personal ID Number"
              name="personal_id_number"
              value={formData.personal_id_number}
              onChange={handleChange}
              fullWidth
              margin="normal"
              variant="outlined"
              InputLabelProps={{ style: { color: 'text.secondary' } }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  '&.Mui-focused fieldset': {
                    borderColor: 'primary.main',
                  },
                },
              }}
            />
            <TextField
              label="First Name"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              fullWidth
              margin="normal"
              variant="outlined"
              InputLabelProps={{ style: { color: 'text.secondary' } }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  '&.Mui-focused fieldset': {
                    borderColor: 'primary.main',
                  },
                },
              }}
            />
            <TextField
              label="Last Name"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              fullWidth
              margin="normal"
              variant="outlined"
              InputLabelProps={{ style: { color: 'text.secondary' } }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  '&.Mui-focused fieldset': {
                    borderColor: 'primary.main',
                  },
                },
              }}
            />
            <TextField
              label="Birth Date"
              name="birth_date"
              type="date"
              value={formData.birth_date}
              onChange={handleChange}
              fullWidth
              margin="normal"
              variant="outlined"
              InputLabelProps={{ style: { color: 'text.secondary' }, shrink: true }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  '&.Mui-focused fieldset': {
                    borderColor: 'primary.main',
                  },
                },
              }}
            />
            <TextField
              label="Height (cm)"
              name="height"
              type="number"
              value={formData.height}
              onChange={handleChange}
              fullWidth
              margin="normal"
              variant="outlined"
              InputLabelProps={{ style: { color: 'text.secondary' } }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  '&.Mui-focused fieldset': {
                    borderColor: 'primary.main',
                  },
                },
              }}
            />
            <TextField
              label="Weight (kg)"
              name="weight"
              type="number"
              value={formData.weight}
              onChange={handleChange}
              fullWidth
              margin="normal"
              variant="outlined"
              InputLabelProps={{ style: { color: 'text.secondary' } }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  '&.Mui-focused fieldset': {
                    borderColor: 'primary.main',
                  },
                },
              }}
            />
            {error && (
              <Typography color="error.main" variant="body2" sx={{ mt: 1 }}>
                {error}
              </Typography>
            )}
          </Box>
          <Stack direction="row" spacing={2} justifyContent="space-between">
            <CancelButton onClick={handleCancel} />
            <Box>
              {!isCreateMode && (
                <DeleteButton onClick={handleDelete} />
              )}
              <SaveButton onClick={handleSubmit} />
            </Box>
          </Stack>
        </Paper>
      </Container>
    </Box>
  );
}