import { Button } from '@mui/material';

interface ListAllButtonProps {
  onClick: () => void;
}

export default function ListAllButton({ onClick }: ListAllButtonProps) {
  return (
    <Button
      variant="contained"
      color="primary"
      onClick={onClick}
      sx={{ textTransform: 'none' }}
    >
      All
    </Button>
  );
}