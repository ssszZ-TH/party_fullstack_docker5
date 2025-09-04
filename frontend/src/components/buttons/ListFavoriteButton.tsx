import { Button } from '@mui/material';

interface ListFavoriteButtonProps {
  onClick: () => void;
}

export default function ListFavoriteButton({ onClick }: ListFavoriteButtonProps) {
  return (
    <Button
      variant="contained"
      color="primary"
      onClick={onClick}
      sx={{ textTransform: 'none' }}
    >
      Favorites
    </Button>
  );
}