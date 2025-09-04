import { Button } from '@mui/material';

interface ListInboxButtonProps {
  onClick: () => void;
}

export default function ListInboxButton({ onClick }: ListInboxButtonProps) {
  return (
    <Button
      variant="contained"
      color="primary"
      onClick={onClick}
      sx={{ textTransform: 'none' }}
    >
      Inbox
    </Button>
  );
}